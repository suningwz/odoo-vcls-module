# -*- coding: utf-8 -*-

#Python Imports
from datetime import datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models

class Employee(models.Model):
    
    _inherit = 'hr.employee'
    
    #################
    # Custom Fields #
    #################
    
    # Connectivity with other systems
    
    employee_external_ID = fields.Integer(
        string='Employee ID',)
    
    link_employee_folder = fields.Char(
        string='Employee Folder',
        help='Paste folder url',
        track_visibility='always',)
    
    # Administrative informations
    
    first_name = fields.Char(
        string='First Name',
        track_visibility='always',)
    
    middle_name = fields.Char(
        string='Middle Name',
        track_visibility='always',)
    
    family_name = fields.Char(
        string='Family Name',
        track_visibility='always',)
    
    family_name_at_birth = fields.Char(
        string='Family Name at Birth',
        track_visibility='always',)
    
    country2_id = fields.Many2one(
        'res.country',
        string='Secondary Citizenship',)
    
    work_permit_expire = fields.Date(
        string='Work Permit Expiring Date',)
    
    private_email = fields.Char(
        related="address_home_id.email",
        string="Private Email",)
    
    private_mobile = fields.Char(
        related="address_home_id.mobile",
        string="Private Mobile",)
    
    ice_contact_relationship = fields.Selection(
        string='Emergency Contact Relationship',
        selection='_selection_relationship',)
    
    #Generic job info (i.e. not linked to the job position object nor the employee contract)
    
    employee_seniority_date = fields.Date(
        string='Employee Seniority Date',
        track_visibility='always',)
    
    employee_start_date = fields.Date(
        string='Employee Start Date',
        track_visibility='always',)
    
    employee_end_date = fields.Date(
        string='Employee End Date',
        track_visibility='always',)
    
    employee_end_reason = fields.Selection(
        string='End Reason',
        selection='_selection_termination',
        track_visibility='always',)
    
    office_id = fields.Many2one(
        'hr.office',
        string='Office',)
    
    #Trial period management
    trial_period_id = fields.Many2one(
        'hr.trial.period',
        string='Trial Period',
        domain="[('company_id', '=', company_id)]",)
    
    trial_start_date = fields.Date(
        string='Trial Period Start Date',)
    
    trial_end_date = fields.Date(
        string='Trial Period End Date',
        compute='_compute_trial_end_date',)
    
    trial_notification_date = fields.Date(
        string='Trial Period Notification Date',
        compute='_compute_trial_end_date',)
    
    #business card fields
    job_info = fields.Char(
        string='Title',
        compute='_set_job_info',
        track_visibility='always',)
    
    diploma_ids = fields.Many2many(
        'hr.diploma',
        string="Diplomas",)
    
    add_private_phone = fields.Boolean(
        string="Add Private Phone",)
    
    #Related to job position(s)
    job_profile_id = fields.Many2one(
        'hr.job_profile',
        string="Current Job Profile",
        track_visibility='always',)
    
    bonus_ids = fields.Many2many(
        'hr.bonus',
        string="Bonuse(s)",
        track_visibility='always',)
    
    #Health Care Management
    last_medical_checkup = fields.Date(
        string="Last Medical Check-up",
        track_visibility='always',)
    
    specific_next_medical_checkup = fields.Date() #used to store manually entered value in the below inverse case
    
    next_medical_checkup = fields.Date(
        string="Next Medical Check-up",
        compute='_get_next_medical_checkup',
        inverse='_set_next_medical_checkup',
        track_visibility='always',)
    
    need_specific_medical = fields.Boolean(
        string="Need Specific Medical Follow-up",
        track_visibility='always',)
    
    #technical fields
    #used to grant access in employee view
    access_level = fields.Selection([
        ('base', 'Base'),
        ('lm', 'Line Manager'),
        ('hr', 'HR'),], 
        compute='_get_access_level',
        store=False,)
    
    lm_ids = fields.Many2many(
        'res.users',
        compute='_get_lm_ids',)
        
    #################################
    # Automated Calculation Methods #
    #################################
    
    @api.depends('parent_id','parent_id.parent_id')
    def _get_lm_ids(self):
        for rec in self:
            empl = rec
            managers = rec.user_id
            while empl.parent_id:
                empl = empl.parent_id
                managers |= empl.user_id
            rec.lm_ids = managers
    
    @api.multi
    def _get_access_level(self):
        for rec in self:
            if rec.user_id.id == self._uid: #for the employee himself
                rec.access_level = 'hr'
                continue
                
            user = self.env['res.users'].browse(self._uid)
            
            #if the user is hr_user, then he grants hr access only if the user is in the same company
            #else, he gets 'lm' access
            if user.has_group('hr.group_hr_user') and (rec.company_id in user.company_ids):
                rec.access_level = 'hr' 
                continue
            elif user.has_group('hr.group_hr_user'):
                rec.access_level = 'lm'
                continue
                
            #if user is an hr manager, then he sees all
            if user.has_group('hr.group_hr_manager'):
                rec.access_level = 'hr'
                continue
            
            # for the management line
            if user in rec.lm_ids:
                rec.access_level = 'lm'
                continue
            
            rec.access_level = 'base'

    #Automatically update the job_info string if one of the component is changed
    @api.depends('job_title','diploma_ids')
    def _set_job_info(self):
        for rec in self:
            rec.job_info = rec.job_title
            if len(rec.diploma_ids) > 0: #If one or more diplomas have been defined, add the separator
                rec.job_info = "{} | ".format(rec.job_info) 
            for id in rec.diploma_ids: #Loop in diplomas to build the string
                rec.job_info = "{} {}".format(rec.job_info, id.name)
    
    # When the nex_medical_checkup is changed, then it is stored on specific_next_medical_checkup
    @api.onchange('next_medical_checkup')
    def _set_next_medical_checkup(self):
        for rec in self:
            rec.specific_next_medical_checkup = rec.next_medical_checkup
    
    # If the last_medical_checkup is updated, then the new one is automatically calculated if the employee does not need specific follow-up
    @api.onchange('last_medical_checkup')
    def _set_specific_next_medical_checkup(self):
        for rec in self:
            if (not rec.need_specific_medical):
                try: rec.specific_next_medical_checkup = rec.last_medical_checkup + relativedelta(years=5)
                except: pass
            
    # Calculate next_medical_checkup according to other fields.
    # Uses try/except to cover cases when fields aren't documented.
    @api.depends('last_medical_checkup','specific_next_medical_checkup')
    def _get_next_medical_checkup(self):
        for rec in self:
            try:
                rec.next_medical_checkup = min(rec.specific_next_medical_checkup, rec.last_medical_checkup + relativedelta(years=5))
            except:
                if rec.last_medical_checkup: 
                    rec.next_medical_checkup = rec.last_medical_checkup + relativedelta(years=5)
                elif rec.specific_next_medical_checkup:
                    rec.next_medical_checkup = rec.specific_next_medical_checkup + relativedelta(years=5)
                else:
                    pass   
    
    #Calculate the Trial Period end date & notification delay
    @api.depends('trial_start_date','trial_period_id','trial_period_id.duration','trial_period_id.notification_delay')
    def _compute_trial_end_date(self):
        for rec in self:
            if rec.trial_start_date and rec.trial_period_id: #if enough info documented
                rec.trial_end_date = rec._get_previous_working_day(rec.trial_start_date + relativedelta(months=rec.trial_period_id.duration))
                rec.trial_notification_date = rec._get_previous_working_day(rec.trial_end_date + relativedelta(days=-1*rec.trial_period_id.notification_delay))
                            
    #####################
    # Selection Methods #
    #####################
    
    @api.model
    def _selection_relationship(self):
        return [
            ('wife_husband','Wife/Husband'),
            ('mother_father','Mother/Father'),
            ('daughter_son','Daughter/Son'),
            ('sister_brother','Sister/Brother'),
            ('partner','Partner'),
            ('friend','Friend'),
            ('neighbour','Neighbour'),
            ('other','Other'),
        ]
    
    @api.model
    def _selection_termination(self):
        return [
            ('termination','Termination'),
            ('resignation','Resignation'),
            ('lay_off','Lay Off'),
            ('retirement','Retirement'),
            ('other','Other'),
        ]
    
    #################
    # Tools Methods #
    #################
    
    def _get_previous_working_day(self,target_date):
        is_worked = False
        while not is_worked:
            bank = False
            if self.env['hr.bank.holiday'].search([('company_id','=',self.company_id.id),('date','=',target_date)]): #check if date is a bank holiday in this company
                bank = True
            if target_date.weekday()<5 and not bank: #this is a worked day
                is_worked = True
                return target_date
            else:
                is_worked = False
                target_date = target_date + timedelta(days=-1)