# -*- coding: utf-8 -*-

#Python Imports
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class LeaveAllocation(models.Model):
    
    _inherit = 'hr.leave.allocation'
   
    
    #As we removed some record rules, let's ensure there's no crosstalk between companies
    @api.constrains('number_of_days')
    def _check_company(self):
        for rec in self:  
            #Ensure the company_id is matching between the employee and the leave type
            if (rec.holiday_type=='employee') and (rec.employee_id.company_id != rec.holiday_status_id.company_id):
                raise ValidationError("The selected leave type for {} - {}.{} is not related to the same company that the selected one ({}).".format(rec.employee_id.name,rec.holiday_status_id.name,rec.holiday_status_id.company_id.name,rec.mode_company_id.name))
                
    ############################
    # OVERRIDE BUSINESS METHOD #
    ############################
    
    """ The below methods are overriden in order to improve the management of child allocation requests.
    - If the parent is turned back to draft, then linked requests aren't unlinked anymore.
    - We test employees to see if a child already exists. If not we create, if yes we keep it without overwriting, except in draft.
    """
    
    #we just comment the unlink line of code
    @api.multi
    def action_draft(self):
        for holiday in self:
            if holiday.state not in ['confirm', 'refuse']:
                raise UserError(_('Leave request state must be "Refused" or "To Approve" in order to reset to Draft.'))
            holiday.write({
                'state': 'draft',
                'first_approver_id': False,
                'second_approver_id': False,
            })
            linked_requests = holiday.mapped('linked_request_ids')
            for linked_request in linked_requests:
                linked_request.action_draft()
            #linked_requests.unlink()
        self.activity_update()
        return True
    
    def _action_validate_create_childs(self):
        
        """ This method is modified in order to be called not only when the parent is validated,
        but also from a CRON related method to ensure that new employee receiving a tag or changing department will receive the proper allocations
        without disturbing the exisitng ones """
        
        childs = self.env['hr.leave.allocation']
        if self.state == 'validate' and self.holiday_type in ['category', 'department', 'company']:
            if self.holiday_type == 'category':
                employees = self.category_id.employee_ids
            elif self.holiday_type == 'department':
                employees = self.department_id.member_ids
            else:
                employees = self.env['hr.employee'].search([('company_id', '=', self.mode_company_id.id)])

            for employee in employees:
                # we test if the employee already has a related child
                existing_child = self.env['hr.leave.allocation'].search([('employee_id', '=', employee.id),('id', 'in', self.linked_request_ids.ids)], limit=1)
                # If there is a child, we edit it if the child is in draft, but we ensure to maintain the already accumulated number of days
                if existing_child:
                    if existing_child.state == 'draft': #if in draft, it means that we want to update it because we turned the parent back to draft
                        values = self._prepare_holiday_values(employee)
                        values.update({
                            'number_of_days': existing_child.number_of_days,
                            'state': 'confirm',
                        })
                        existing_child.write(values)
                        childs += existing_child
                
                else: #we need to create a new one
                    childs += self.with_context(
                        mail_notify_force_send=False,
                        mail_activity_automation_skip=True,
                        mail_create_nosubscribe=True
                    ).create(self._prepare_holiday_values(employee))
                
            # TODO is it necessary to interleave the calls?
            childs.action_approve()
            if childs and self.holiday_status_id.validation_type == 'both':
                childs.action_validate()
        return childs
    
    
    ################
    # CRON METHODS #
    ################
    
    @api.model
    def _update_child_allocations(self):
        """
        Methods called by CRON task in order to ensure that employees with new category/department/company
        is granted with the proper leave allocations 
        """
        #we search for the proper allocations (i.e. possibly having childs)
        allocs = self.search([('state', '=', 'validate'),('holiday_type', 'in', ['category', 'department', 'company'])])
        
        for alloc in allocs:
            alloc._action_validate_create_childs()
        
    
    #the original method is overriden in order to synchronize the nexcalls to the last day of the month and use the employee start date.
    # We want to execute only the last day of the month in order to synchronise all holidays
    @api.model
    def _update_accrual(self):
        """
            Method called by the cron task in order to increment the number_of_days when
            necessary.
        """
        today = fields.Date.from_string(fields.Date.today())

        holidays = self.search([('accrual', '=', True), ('state', '=', 'validate'), ('holiday_type', '=', 'employee'),
                                '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
                                '|', ('nextcall', '=', False), ('nextcall', '<=', today)])

        for holiday in holidays:
            values = {}

            delta = relativedelta(days=0)
            
            #in case of months, we define the period start as the 1st day of the month and the period end the last day of the month       
            if holiday.interval_unit == 'months' and holiday.interval_number==1:
                period_start = datetime.combine(today.replace(day=1), time(0, 0, 0))
                period_end = datetime.combine(today.replace(day=1,month=(today.month + 1)), time(0, 0, 0)) - relativedelta(days=1)
                
                #if this is the 1st execution for this holiday (i.e. nexcall = False), then we postpone to the end of current month
                if not holiday.nextcall:
                    values['nextcall'] = period_end
                    holiday.write(values)
                    continue
                #if there's a nextcall, it means that today is the last day of the month
                else:
                    values['nextcall'] = datetime.combine(today.replace(day=1,month=(today.month + 2)), time(0, 0, 0)) - relativedelta(days=1)

                
            else :
                if holiday.interval_unit == 'weeks':
                    delta = relativedelta(weeks=holiday.interval_number)
                if holiday.interval_unit == 'month':
                    delta = relativedelta(months=holiday.interval_number)
                if holiday.interval_unit == 'years':
                    delta = relativedelta(years=holiday.interval_number)
                    
                values['nextcall'] = (holiday.nextcall if holiday.nextcall else today) + delta
                period_start = datetime.combine(today, time(0, 0, 0)) - delta
                period_end = datetime.combine(today, time(0, 0, 0)) 
                raise UserError('nextcall %s' % (period_end))
                
            # We have to check when the employee has started
            # in order to not allocate him/her too much leaves
            creation_date = fields.Datetime.from_string(holiday.employee_id.employee_start_date)

            # If employee is created after the period, we cancel the computation
            if period_end <= creation_date:
                holiday.write(values)
                continue

            # If employee created during the period, taking the date at which he has been created
            if period_start <= creation_date:
                period_start = creation_date

            worked = holiday.employee_id.get_work_days_data(period_start, period_end, domain=[('holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')])['days']
            left = holiday.employee_id.get_leave_days_data(period_start, period_end, domain=[('holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')])['days']
            prorata = worked / (left + worked) if worked else 0

            days_to_give = holiday.number_per_interval
            if holiday.unit_per_interval == 'hours':
                # As we encode everything in days in the database we need to convert
                # the number of hours into days for this we use the
                # mean number of hours set on the employee's calendar
                days_to_give = days_to_give / (holiday.employee_id.resource_calendar_id.hours_per_day or HOURS_PER_DAY)

            values['number_of_days'] = holiday.number_of_days + days_to_give * prorata
            if holiday.accrual_limit > 0:
                values['number_of_days'] = min(values['number_of_days'], holiday.accrual_limit)

            holiday.write(values)
    
    #we don't want LM approval for allocations
    def _get_responsible_for_approval(self):
        return self.env.user
   
    
    #we don't want the employee to be notified
    @api.multi
    def add_follower(self, employee_id):
        pass
        '''
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe(partner_ids=employee.user_id.partner_id.ids)
        '''
    
    
    #we suppress every related notifications
    def activity_update(self):
        pass
        '''
        to_clean, to_do = self.env['hr.leave.allocation'], self.env['hr.leave.allocation']
        for allocation in self:
            if allocation.state == 'draft':
                to_clean |= allocation
            elif allocation.state == 'confirm':
                allocation.activity_schedule(
                    'hr_holidays.mail_act_leave_allocation_approval',
                    user_id=allocation.sudo()._get_responsible_for_approval().id)
            elif allocation.state == 'validate1':
                allocation.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval'])
                allocation.activity_schedule(
                    'hr_holidays.mail_act_leave_allocation_second_approval',
                    user_id=allocation.sudo()._get_responsible_for_approval().id)
            elif allocation.state == 'validate':
                to_do |= allocation
            elif allocation.state == 'refuse':
                to_clean |= allocation
        if to_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_allocation_approval', 'hr_holidays.mail_act_leave_allocation_second_approval'])
        if to_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval', 'hr_holidays.mail_act_leave_allocation_second_approval'])
        
        '''