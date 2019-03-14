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
    def get_employee_info(self,):
        for l in self:
            #employee
            l.employee_external_id = l.employee_id.employee_external_id
            l.location =  l.employee_id.office_id.name
            l.first_name = l.employee_id.first_name
            l.middle_name = l.employee_id.middle_name
            l.family_name = l.employee_id.family_name
            
            #relevant contract is maybe not the one active today, it depends on the date_start of the contract
            contract = self.env['hr.contract'].search([('employee_id','=',l.employee_id.id),('date_start','<=',l.export_id.end_date)],order='date_start desc')[0]
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
                leave.trunc_duration = leave.employee_id.get_leaves_distribution(leave.trunc_start, leave.trunc_end)['leave']
                """
                if leave.employee_id.first_name == 'Coralie':
                    raise ValidationError("from {} to {} | {}".format(leave.trunc_start, leave.trunc_end,leave.employee_id.get_leaves_distribution(leave.trunc_start, leave.trunc_end)))
                """
                
                leave.export_string = "From {} to {} | {} {} ".format(leave.trunc_start, leave.trunc_end,leave.trunc_duration,leave.holiday_status_id.name)
                #Add Info for exceptional leaves
                if leave.exceptional_case_id: #if it is an exceptional case
                    leave.export_string += "({} - {})".format(leave.exceptional_category_id,leave.exceptional_case_id)
                elif leave.exceptional_category_id: #if exceptional category only
                    leave.export_string += "({})".format(leave.exceptional_category_id)
                    
    @api.multi
    def get_leaves_info(self):
        for l in self:
            
            """
            if l.first_name == 'Cansu':
                raise ValidationError('{}'.format(l.leave_ids.mapped('export_string')))
            """
            
            leaves = l.leave_ids.filtered(lambda r: r.holiday_status_id.payroll_type == 'rtt')
            if leaves:
                l.rtt_paid_days = sum(leaves.mapped('trunc_duration'))
                l.rtt_paid_info = '\n'.join(leaves.mapped('export_string'))
            
            leaves = l.leave_ids.filtered(lambda r: r.holiday_status_id.payroll_type == 'cp_paid')
            if leaves:
                l.cp_paid_days = sum(leaves.mapped('trunc_duration'))
                l.cp_paid_info = '\n'.join(leaves.mapped('export_string'))
            
            leaves = l.leave_ids.filtered(lambda r: r.holiday_status_id.payroll_type == 'cp_unpaid')
            if leaves:
                l.cp_unpaid_days = sum(leaves.mapped('trunc_duration'))
                l.cp_unpaid_info = '\n'.join(leaves.mapped('export_string'))
                
            leaves = l.leave_ids.filtered(lambda r: r.holiday_status_id.payroll_type == 'sick')
            if leaves:
                l.sick_days = sum(leaves.mapped('trunc_duration'))
                l.sick_info = '\n'.join(leaves.mapped('export_string'))
                
            leaves = l.leave_ids.filtered(lambda r: r.holiday_status_id.payroll_type == 'other_paid')
            if leaves:
                l.other_paid_days = sum(leaves.mapped('trunc_duration'))
                l.other_paid_info = '\n'.join(leaves.mapped('export_string'))
