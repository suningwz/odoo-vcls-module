# -*- coding: utf-8 -*-
#Python Imports
from datetime import date, datetime, time
#Odoo Imports
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PayrollLine(models.Model):
    _name = 'export.payroll.line'
        
    """ This model represents a line in a monthly payroll, corresponding to the status of an employee per month."""

    name = fields.Char(
        readonly = True,
        )
    
    active = fields.Boolean(
        related = 'export_id.active',
        store = True,
        )
    
    ### TRACEABILITY FIELDS 
    export_id = fields.Many2one(
        'export.payroll',
        string = 'Parent Export',
        required = True,
        readonly = True,
        )
    
    is_locked = fields.Boolean(
        readonly=True,
        related='export_id.is_generated',
        )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string = 'Employee',
        readonly = True,
        required = True,
        )
    
    leave_ids = fields.Many2many(
        'hr.leave',
        string = 'Related Leaves',
        readonly = True,
        )
    
    currency_id = fields.Many2one(
        'res.currency',
        related = 'export_id.currency_id',
        readonly=True,
        required=True,
    )
    
    ### EMPLOYEE FIELDS
    employee_external_id = fields.Char(readonly=True)
    location = fields.Char(readonly=True) #employee_id.office_id
    first_name = fields.Char(readonly=True) 
    middle_name = fields.Char(readonly=True) 
    family_name = fields.Char(readonly=True)
    contract_type = fields.Char(readonly=True) #from contract_id
    working_percentage = fields.Float(readonly=True) #from contract_id.resource_calendar_id.effective_percentage >> widget percentage
    status = fields.Char(readonly=True) # newcomer or not
    
    ### PACKAGE FIELDS
    fulltime_salary = fields.Monetary(readonly=True) #contract_id.fulltime_salary
    prorated_salary = fields.Monetary(readonly=True) #contract_id.prorated_salary
    total_bonus = fields.Monetary(readonly=True) #sum bonus per employee over dates (included)
    car_allowance = fields.Monetary(readonly=True) #sum benefit_id.car_allowance for benefit employee_id >> order date descending (limit=1)
    transport_allowance = fields.Monetary() #sum benefit_id.transport_allowance for benefit employee_id >> order date descending (limit=1)
    lunch_ticket = fields.Integer()
    extra_amount = fields.Monetary(default = 0) #0 by default, editable
    
    ### EXTRA FIELDS
    comments = fields.Char()
    
    ###LEAVE FIELDS
    rtt_paid_days = fields.Float(readonly=True, default=0) # Changed to float because 0.5 day
    rtt_paid_info = fields.Char(readonly=True, default='-') #text from/to + leave type name + total days
    rtt_paid_balance = fields.Float(readonly=True, default=0)

    cp_paid_days = fields.Float(readonly=True, default=0)
    cp_paid_info = fields.Char(readonly=True, default='-')

    cp_unpaid_days = fields.Float(readonly=True, default=0)
    cp_unpaid_info = fields.Char(readonly=True, default='-')

    sick_days = fields.Float(readonly=True, default=0)
    sick_info = fields.Char(readonly=True, default='-')

    other_paid_days = fields.Float(readonly=True, default=0)
    other_paid_info = fields.Char(readonly=True, default='-')
    
    @api.model
    def create(self,vals):         
        # Get principal values
        line = super().create(vals)
        line.comments = ""
        
        #Populate employee related info
        line.get_employee_info()
        #populate leaves related info
        line.process_leaves()
        line.get_leaves_info()
        
        # Compute name
        line.name = '{}-{}'.format(line.export_id.name,line.employee_external_id)
        return line
    
    @api.multi
    def get_employee_info(self):
        for l in self:
            #employee
            l.employee_external_id = l.employee_id.employee_external_id
            l.location =  l.employee_id.office_id.name
            l.first_name = l.employee_id.first_name
            l.middle_name = l.employee_id.middle_name
            l.family_name = l.employee_id.family_name
            
            #relevant contract is maybe not the one active today, it depends on the date_start of the contract
            try:
                contract = self.env['hr.contract'].search([('employee_id','=',l.employee_id.id),('date_start','<=',l.export_id.end_date)],order='date_start desc')[0]
            except:
                raise ValidationError(' No Valid Contract Found for {}'.format(l.employee_id.name))
            l.contract_type =  contract.type_id.name
            l.working_percentage = contract.resource_calendar_id.effective_percentage
            l.fulltime_salary = contract.fulltime_salary
            l.prorated_salary = contract.prorated_salary
            
            #we get the status of the employee based on contract dates
            l.status = 'IN'
            # if the relevant contract has started during the period
            if contract.date_start >= l.export_id.start_date:
                # if there was already a contract before the relevant one, then it's a contract change. Else, this is a newcomer:
                if self.env['hr.contract'].search([('employee_id','=',l.employee_id.id),('date_start','<',contract.date_start)]):
                    l.status = 'CONTRACT CHANGE'
                    l.comments += 'Contract Changed on {} \n'.format(contract.date_start)
                else:
                    l.status = 'NEWCOMER'
                    l.comments += 'Start Date {} \n'.format(contract.date_start)
            
            #bonus info: get the ones allocated within the defined period to the employee
            bonuses = self.env['hr.bonus'].search([('employee_id','=',l.employee_id.id),('date','>=',l.export_id.start_date),('date','<=',l.export_id.end_date)])
            l.total_bonus = sum(bonuses.mapped('amount'))
            
            #benefits info: get the most recent one
            benefit = self.env['hr.benefit'].search([('employee_id','=',l.employee_id.id),('date','<=',l.export_id.end_date)],order='date desc', limit=1)
            l.car_allowance = sum(benefit.mapped('car_allowance'))
            l.transport_allowance = sum(benefit.mapped('transport_allowance'))        

    
    @api.multi
    def process_leaves(self):
        for l in self:
            # We select all the validated leaves for the employee, which are starting before the end of the period AND ending after the start of the period.
            leaves = self.env['hr.leave'].search([('employee_id','=',l.employee_id.id),('date_to','>=',l.export_id.start_date),('date_from','<=',l.export_id.end_date),('state','=','validate')])
            l.write({'leave_ids': [(6, 0, leaves.mapped('id'))]})
            
            #loop in leaves to process it
            for leave in leaves:
                leave.trunc_start = max(leave.date_from.date(),l.export_id.start_date)
                leave.trunc_end = min(leave.date_to.date(),l.export_id.end_date)
                if leave.request_unit_half :
                    leave.trunc_duration = 0.5
                else:
                    leave.trunc_duration = leave.employee_id.get_leaves_distribution(leave.trunc_start, leave.trunc_end)['leave']
                
                leave.export_string = "From {} to {} | {} {} ".format(leave.trunc_start, leave.trunc_end,leave.trunc_duration,leave.holiday_status_id.name)
                #Add Info for exceptional leaves
                if leave.exceptional_case_id: #if it is an exceptional case
                    leave.export_string += "({} - {})".format(leave.exceptional_category_id,leave.exceptional_case_id)
                elif leave.exceptional_category_id: #if exceptional category only
                    leave.export_string += "({})".format(leave.exceptional_category_id)
                    
    @api.multi
    def get_leaves_info(self):
        for l in self:
            
            aggregate = l.aggregate_payroll_type('rtt')
            l.rtt_paid_days = aggregate['days']
            l.rtt_paid_info = aggregate['info']
            
            aggregate = l.aggregate_payroll_type('cp_paid')
            l.cp_paid_days = aggregate['days']
            l.cp_paid_info = aggregate['info']
            
            aggregate = l.aggregate_payroll_type('cp_unpaid')
            l.cp_unpaid_days = aggregate['days']
            l.cp_unpaid_info = aggregate['info']
            
            aggregate = l.aggregate_payroll_type('sick')
            l.sick_days = aggregate['days']
            l.sick_info = aggregate['info']
            
            aggregate = l.aggregate_payroll_type('other_paid')
            l.other_paid_days = aggregate['days']
            l.other_paid_info = aggregate['info']
            
    
    def aggregate_payroll_type(self,payroll_type,get_balance = False):
        self.ensure_one()
        leaves = self.leave_ids.filtered(lambda r: r.holiday_status_id.payroll_type == payroll_type)
        
        """
        if get_balance:
            #we get past leaves that have not been truncated
            past_leaves = self.env['hr.leave'].search([('employee_id','=',self.employee_id.id)]) - leaves
        """
        
        if leaves:
            return {
                'days': sum(leaves.mapped('trunc_duration')),
                'info': '\n'.join(leaves.mapped('export_string')),
            }
        
        else:
            return {
                'days': 0,
                'info': '',
            }