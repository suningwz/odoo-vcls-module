# -*- coding: utf-8 -*-

#Python Imports
from datetime import date, datetime, time
#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

class Leave(models.Model):
    _inherit = 'hr.leave'
    
    
    ####################
    # Overriden Fields #
    ####################
    #holiday_status_id = fields.Many2one(
    #    default=False)
   
    #################
    # Custom Fields #
    #################
    
    related_type_name = fields.Char( #only used for the view customization (visibility if type = ...)
        related='holiday_status_id.name', 
        string='Type Name',)
    
    exceptional_category_id = fields.Many2one(
        'hr.exceptional.leave.category', 
        string="Exceptional Leave Category",
        domain="[('leave_type_id', '=', holiday_status_id)]",) #ensure company coherence throught the leave_type_ID, whih is linked to a company
    
    exceptional_case_id = fields.Many2one(
        'hr.exceptional.leave.case',
        string="Exceptional Leave Case",
        domain="[('category_id', '=', exceptional_category_id)]",) #ensure proper subcategory
    
    exceptional_allocation = fields.Float(
        string='Exceptional Allocation',
        compute='_compute_exceptional_allocation',)
    
    employee_company_id = fields.Many2one(
        related='employee_id.company_id',
        String='Employee Company',)
    
    future_number_of_days = fields.Float(
        string="Projected Days",
        compute='_compute_future_days',)
    
    future_number_of_days_info = fields.Char(
        string="Info",
        compute='_compute_future_days',)
    
    is_accrual = fields.Boolean(
        default=False)
    
    
    #######################
    # Calculation Methods #
    #######################
    
    # Update the available case list according to the selected category
    @api.depends('exceptional_category_id','exceptional_case_id')
    def _compute_exceptional_allocation(self):
        for rec in self:
            if rec.exceptional_case_id: 
                rec.exceptional_allocation = rec.exceptional_case_id.max_allocated_days
            elif rec.exceptional_category_id:
                rec.exceptional_allocation = rec.exceptional_category_id.default_max_allocated_days
    
    # Compute an expected number of days at request start date according to ongoing allocations
    @api.depends('request_date_from','holiday_status_id')
    def _compute_future_days(self):
        for rec in self:
            
            #get remaining days
            leave_days = rec.holiday_status_id.get_days(rec.employee_id.id)[rec.holiday_status_id.id]['virtual_remaining_leaves']
            
            #get all the active leave allocations for the corresponding leave type and user
            allocs =  rec.env['hr.leave.allocation'].search([('employee_id','=',rec.employee_id.id),('holiday_status_id','=',rec.holiday_status_id.id),('accrual','=',True),('state','=','validate'),('interval_unit','=','months')])
            #allocs =  rec.env['hr.leave.allocation'].search([('employee_id','=',rec.employee_id.id),('holiday_status_id','=',rec.holiday_status_id.id),('date_to', '>', fields.Datetime.now()),('interval_unit','=','months'),('interval_number','=',1),('unit_per_interval','=','days')])
            
            #sum exisiting allocations
            monthly_add = 0.0
            end_alloc = rec.date_from
            rec.is_accrual = False
            for alloc in allocs:  
                monthly_add += alloc.number_per_interval
                rec.is_accrual = True
                if alloc.date_to:
                    end_alloc = alloc.date_to
            
            #Compute the number of intervals between today() and the leave start date.
            # If the en d of the accrual 
            start_ord = date.today().toordinal()
            end_ord = min(rec.date_from.toordinal(),end_alloc.toordinal())
            cnt = 0
            
            for d_ord in range(start_ord,end_ord+1): #1 is added to ensure the last day of the range to be taken in account
                d = date.fromordinal(d_ord+1) #we check if the day after is the 1st of the month, in order to count the last days of the previous month
                if (d.day==1): cnt = cnt + 1 #if it is the 1t day of the month, we increment the counter    
            
            #turn on the is_accrual to prompt complementary info in view
            #if monthly_add>0.0:
                
            
            rec.future_number_of_days = round(leave_days + cnt*monthly_add,2)
            rec.future_number_of_days_info="{} days available today + {} x {} days to be earned before {} = {} total days".format(len(allocs),cnt,monthly_add,min(rec.date_from.date(),end_alloc.date()),rec.future_number_of_days)

            
    #clear the case id when the category changes
    @api.onchange('exceptional_category_id')
    def _clear_exceptional_case(self):
        for rec in self:
            rec.exceptional_case_id = False
    
    ####################
    # Checking Methods #
    ####################
    
    #In case of exceptional absences, check if the allocated amount is sufficient
    @api.constrains('number_of_days')
    def _check_exceptional_absence(self):
        for rec in self:
            if rec.related_type_name == 'Exceptional Leave': #in case of exceptional absence
                if rec.number_of_days > rec.exceptional_allocation:
                    raise ValidationError("The selected number of days is above the allocation of the defined Exceptional Leave ({} days). Please correct.".format(rec.exceptional_allocation))
    
    #Restrict date creation (Not before tomorrow) if the user is not a leave manager
    @api.constrains('date_from')
    def _check_role_restriction(self):
        for rec in self:
            if not self.env.user.has_group('base.group_leave_manager'): #to be udated to match the proper group
                if rec.date_from.date() <= date.today():
                    raise ValidationError("You can't create a request for today or an earlier date. Please contact HR.")
                    
    #Ensure the company_id is matching between the employee and the leave type
    @api.constrains('holiday_status_id')
    def _check_company_id(self):
        for rec in self:
            if (rec.holiday_type=='By Employee') and (rec.employee_company_id != rec.holiday_status_id.company_id): #only if it's a request by employee
                raise ValidationError("The selected leave type is not related to the same company that the selected employee.")
    
    # Overriding the initial number of days constrains to match with future days
    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        
        for rec in self:
            if rec.holiday_type != 'employee' or not rec.employee_id or rec.holiday_status_id.allocation_type == 'no':
                continue
                
            if rec.future_number_of_days < rec.number_of_days:
                raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                        'Please also check the leaves waiting for validation.'))