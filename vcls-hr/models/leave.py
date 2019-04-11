# -*- coding: utf-8 -*-

#Python Imports
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

class Leave(models.Model):
    _inherit = 'hr.leave'
    
    
    ############################
    # Overriden Default Methods #
    ############################
    @api.model
    def default_get(self, fields_list):
        defaults = super(Leave, self).default_get(fields_list)
        defaults = self._default_get_request_parameters(defaults)

        LeaveType = self.env['hr.leave.type'].with_context(employee_id=defaults.get('employee_id'), default_date_from=defaults.get('date_from', fields.Datetime.now().date()))
        lt = LeaveType.search([('valid', '=', True)])

        #defaults['holiday_status_id'] = lt[0].id if len(lt) > 0 else defaults.get('holiday_status_id')
        defaults['holiday_status_id'] = False
        return defaults
   
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
    
    lm_user_id = fields.Many2one(
        'res.users',
        related='employee_id.parent_id.user_id',)
    
    head_user_id = fields.Many2one(
        'res.users',
        related='department_id.manager_id.user_id')
    
    future_number_of_days = fields.Float(
        string="Projected Days",
        compute='_compute_future_days',)
    
    future_number_of_days_info = fields.Char(
        string="Info",
        compute='_compute_future_days',)
    
    is_accrual = fields.Boolean(
        default=False)
    
    max_credit = fields.Float(
        compute='_compute_future_days',
        )
    
    start_date = fields.Date(
        compute='_compute_dates',
        readonly=True,)
    
    #####################
    # Overriden Methods #
    #####################
    #We simplify this method to force the number of days to be based on days and not hours.
    def _get_number_of_days(self, date_from, date_to, employee_id):
        # Returns a float equals to the timedelta between two dates given as string.
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            
            start = datetime.combine(date_from.date(), time.min)
            stop = datetime.combine(date_to.date(), time.max)
            #return employee.get_work_days_data(date_from, date_to)['days']
            
            # cover the case of half a day on days  OFF
            delta = max(0,employee.get_work_days_data(start, stop)['days'] - (0.5 if self.request_unit_half else 0.0)) 
            return delta
            #return employee.get_work_days_data(start, stop)['days']
        
        today_hours = self.env.user.company_id.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(), time.min),
            datetime.combine(date_from.date(), time.max),
            False)

        return self.env.user.company_id.resource_calendar_id.get_work_hours_count(date_from, date_to) / (today_hours or HOURS_PER_DAY)
        
        """
        delta = date_to.date()-date_from.date()
        if self.request_unit_half:
            in_days = 0.5 #half a day is half a day
        else:
            in_days = delta.days + 1 #we add one to cover the current day (i.e. if start = end date)
        
        return in_days
        """
        
    def activity_update(self):
        default_deadline = datetime.today() + relativedelta(weeks=1)
        to_clean, to_do = self.env['hr.leave'], self.env['hr.leave']
        for holiday in self:
            if holiday.state == 'draft':
                to_clean |= holiday
            elif holiday.state == 'confirm':
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_approval',
                    user_id=holiday.sudo()._get_responsible_for_approval().id,
                    date_deadline=default_deadline)
            elif holiday.state == 'validate1':
                holiday.activity_feedback(['hr_holidays.mail_act_leave_approval'])
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_second_approval',
                    user_id=holiday.sudo()._get_responsible_for_approval().id,
                     date_deadline=default_deadline)
            elif holiday.state == 'validate':
                to_do |= holiday
            elif holiday.state == 'refuse':
                to_clean |= holiday
        if to_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
        if to_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
            
    
    #we call the parent one and clean the holiday_status_id
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        super()._onchange_employee_id
        if self.employee_id:
            self.mode_company_id = self.employee_id.company_id

    
    #######################
    # Calculation Methods #
    #######################
    
    #update the date fields to be used n kanban views to hide time value
    @api.depends('date_from','date_to')
    def _compute_dates(self):
        for rec in self:
            rec.start_date = rec.date_from.date()
    
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
            
            if not rec.holiday_status_id: #i.e. if no type defined, then continue
                continue
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
                    
            #if negative is authorized, this means we compute the future number of days for the last day of the planned accrual
            cnt2 = 0
            if rec.holiday_status_id.authorize_negative:
                end_ord = end_alloc.toordinal()
                for d_ord in range(start_ord,end_ord+1): #1 is added to ensure the last day of the range to be taken in account
                    d = date.fromordinal(d_ord+1) #we check if the day after is the 1st of the month, in order to count the last days of the previous month
                    if (d.day==1): cnt2 = cnt2 + 1 #if it is the 1t day of the month, we increment the counter
                        
            #turn on the is_accrual to prompt complementary info in view
            #if monthly_add>0.0:
            rec.future_number_of_days = round(leave_days + cnt*monthly_add,2)
            rec.max_credit = round(leave_days + cnt2*monthly_add,2)
            rec.future_number_of_days_info="{} days will be available on {}.".format(rec.future_number_of_days,rec.date_from.date())
            
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
            if not self.env.user.has_group('vcls-hr.vcls_group_HR_local'): #to be udated to match the proper group
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

            #if the current user is member of HR, then bypass the validation.
            if self.env.user.has_group('vcls-hr.vcls_group_HR_local'):
                continue
            
            #if the holiday type authorizes to take credit, then the limit is the calculated max credit
            if rec.holiday_status_id.authorize_negative:
                limit = rec.max_credit
            else: #else this is the future number of days
                limit = rec.future_number_of_days
                
            if  (limit + rec.number_of_days) < rec.number_of_days: #we add number_of_days becaus the virtual remaining leaves is already updated when we test this part of the code
                raise ValidationError('The number of remaining leaves ({} days) is currently not sufficient for this leave type.\n'
                                        'Please contact your local HR representative for particular case management.'.format(round(limit + rec.number_of_days,2)))