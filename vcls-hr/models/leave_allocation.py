# -*- coding: utf-8 -*-

#Python Imports
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class LeaveAllocation(models.Model):
    
    _inherit = 'hr.leave.allocation'
   
    #used to customise selection domain according to the selected employee company
    employee_company_id = fields.Many2one(
        related='employee_id.company_id',
        String='Employee Company',)
    
    #As we removed some record rules, let's ensure there's no crosstalk between companies
    @api.constrains('number_of_days')
    def _check_company(self):
        for rec in self:  
            #Ensure the company_id is matching between the employee and the leave type
            if (rec.holiday_type=='employee') and (rec.employee_company_id != rec.holiday_status_id.company_id):
                raise ValidationError("The selected leave type is not related to the same company that the selected employee.")
    
    ########################
    # OVERRIDE CRON METHOD #
    ########################
    
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
    