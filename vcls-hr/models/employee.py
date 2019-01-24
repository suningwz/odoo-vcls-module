# -*- coding: utf-8 -*-

#Python Imports
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models

class Employee(models.Model):
    
    _inherit = 'hr.employee'
    _sql_constraints = [
                     ('employee_external_id_unique', 
                      'unique(employee_external_id)',
                      'Employee ID is not unique.')
                    ]
    
    #################
    # Custom Fields #
    #################
    
    # Connectivity with other systems
    
    employee_external_id = fields.Char(
        string='Employee ID',
        default="/",)
    
    link_employee_folder = fields.Char(
        string='Employee Folder',
        help='Paste folder url',
        track_visibility='always',)
    
    # Overriden fields
    name = fields.Char()
    
    gender = fields.Selection(
        default=False,)
     
    resource_calendar_id = fields.Many2one(
        related = 'contract_id.resource_calendar_id',
        readonly=True,)
    
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
    
    # private info, to be overriden in the read function according to the read access
    
    family_name_at_birth = fields.Char(
        string='Family Name at Birth',
        track_visibility='always',)
    
    country2_id = fields.Many2one(
        'res.country',
        string='Secondary Citizenship',)
    
    work_permit_expire = fields.Date(
        string='Work Permit Expiring Date',)
    
    street = fields.Char(
        string='Street',)
    
    street2 = fields.Char(
        string='Street 2',)
    
    city = fields.Char()
    
    state_id = fields.Many2one(
        'res.country.state',
        string = 'State')
    
    zip = fields.Char(
        string='ZIP',)
    
    address_country_id = fields.Many2one(
        'res.country',
        string="Country",)
    
    private_email = fields.Char(
        string="Private Email",)
    
    private_mobile = fields.Char(
        string="Private Mobile",)
    
    private_phone = fields.Char(
        string='Private Phone',)
    
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
        related='contract_id.job_profile_id',
        string="Current Job Profile",
        track_visibility='always',)
    
    bonus_ids = fields.Many2many(
        'hr.bonus',
        string="Over Variable Salary",
        compute = "_get_bonuses",)
    
    contract_ids = fields.Many2many(
        'hr.contract',
        string="Contract(s)",
        compute = "_get_contracts",)
    
    #Benefit related
    benefit_ids = fields.Many2many(
        'hr.benefit',
        string = "Benefits",
        compute = '_get_benefits',)
    
    '''
    #Benefits
    car_info = fields.Char(
        string='Company car',
        compute='_get_car_info',
        )
    '''
   
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
    
    affiliation_date = fields.Date(
        string='Affiliation Date',)
    
    affiliated_company = fields.Char(
        string='Affiliated Company')
    
    medical_policy_number = fields.Char(
        string='Medical Policy Number',)
    
    #technical fields
    #used to grant access in employee view
    access_level = fields.Selection([
        ('base', 'Base'),
        ('lm', 'Line Manager'),
        ('hl', 'Hierarchical Line'),
        ('hr', 'HR'),
        ('me','Me'),
        ('support', 'Support'),], 
        compute='_get_access_level',
        store=False,
        default='hr',)
    
    lm_ids = fields.Many2many(
        'res.users',
        compute='_get_lm_ids',)
    
    country_name = fields.Char(
        related='company_id.country_id.name',)
    
    employee_status = fields.Selection([
        ('future','Future'),
        ('active','Active'),
        ('departed','Departed')],
        default = 'future',
        )
    
    
    ################
    # CRUD Methods #
    ################
    
    #At Employee creation, create a default contract
    @api.model
    def create(self,vals):
        
        #if no external ID defined, then increment using the sequence
        if vals.get('employee_external_id','/')=='/':
            vals['employee_external_id'] = self.env['ir.sequence'].next_by_code('seq_hr_employee_ext_id')
        
        #enter default value in first, middle, family names
        names = vals.get('name','').split(' ')
        if len(names) == 2:
            vals.update({
                'first_name':names[0],
                'family_name':names[1],
            })
        elif len(names) == 3:
            vals.update({
                'first_name':names[0],
                'middle_name':names[1],
                'family_name':names[2],
            })
            
        empl=super().create(vals)
        
        '''
        #create the related default contract
        contract = self.env['hr.contract'].create(
            {
                'name':"{} | 01".format(empl.name),
                'employee_id':empl.id,
                'wage':0,
            }
        )
        '''

        return empl
        
    #################################
    # Automated Calculation Methods #
    #################################
    
    #adds or remove from the lm group according to the subortinates count
    @api.model #to be called from CRON job
    def _check_lm_membership(self):
        group = self.env.ref('vcls-hr.vcls_group_lm')
        user = self.user_id
        if self.child_ids[0]: #if a child is found
            vals = {'groups_id': [(4, group.id)]}
        else:
            vals = {'groups_id': [(3, group.id)]}
                
        user.write(vals)
            
    
    
    @api.model #to be called from CRON job
    def _check_employee_status(self):
        date_ref = date.today()
        employees = self.env['hr.employee'].search([])
        for empl in employees:
            if empl.employee_end_date: #if end date configured
                if empl.employee_end_date <= date_ref:
                    empl.employee_status = 'departed'
                    continue
                else: #end date is documented but in the fulture
                    empl.employee_status = 'active'
                    continue
                    
            elif empl.employee_start_date: #if start date documented
                if empl.employee_start_date > date_ref: #employee to start in the future
                    empl.employee_status = 'future'
                else:
                    empl.employee_status = 'active'
                    
            else:
                empl.employee_status = False #no dates = no status
    
    @api.multi
    def _get_benefits(self):
        for empl in self:
            empl.benefit_ids = self.env['hr.benefit'].search([('employee_id','=',empl.id)])

    @api.multi
    def _get_bonuses(self):
        for empl in self:
            empl.bonus_ids = self.env['hr.bonus'].search([('employee_id','=',empl.id)])
    
    @api.multi
    def _get_contracts(self):
        for empl in self:
            empl.contract_ids = self.env['hr.contract'].search([('employee_id','=',empl.id)])
    
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
                rec.access_level = 'me'
                continue
                
            user = self.env['res.users'].browse(self._uid)
            
            #if user is in support group
            if user.has_group('base.group_erp_manager'):
                rec.access_level = 'support'
                continue
            
            #if user is an hr manager, then he sees all
            if user.has_group('vcls-hr.vcls_group_HR_global'):
                rec.access_level = 'hr'
                continue
            
            #if the user is hr_user, then he grants hr access only if the user is in the same company
            #else, he gets 'lm' access
            if user.has_group('vcls-hr.vcls_group_HR_local') and (rec.company_id in user.company_ids):
                rec.access_level = 'hr' 
                continue
                
            elif user.has_group('vcls-hr.vcls_group_HR_local'):
                rec.access_level = 'hl'
                continue
            
            # grant extended lm access to head of activity, head of department, and N+1
            if (user == rec.parent_id.user_id) or (user == rec.contract_id.job_profile_id.job1_head.user_id) or (user == rec.contract_id.job_profile_id.job2_head.user_id) or (user == rec.contract_id.job_profile_id.job1_dir.user_id) or (user == rec.contract_id.job_profile_id.job2_dir.user_id):
                rec.access_level = 'lm'
                continue
                
            # for the management line
            elif user in rec.lm_ids:
                rec.access_level = 'hl'
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
                #add a one day offset
                rec.trial_end_date = rec._get_previous_working_day(rec.trial_start_date + relativedelta(months=rec.trial_period_id.duration,days=-1))
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
        
    ##########################
    # Pop-up windows Methods #
    ##########################
    
    def new_bonus_pop_up(self):
        return {
            'name': 'Create a new over variable salary',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'hr.bonus',
            'type': 'ir.actions.act_window',
            'context': "{{'default_employee_id': {}}}".format(self.id),
        }
    
    def new_contract_pop_up(self):
        view_id = self.env.ref('vcls-hr.vcls_contract_form1').id
        count = len(self.env['hr.contract'].search([('employee_id','=',self.id)]))
        contract_name = "{} | {:02}".format(self.name,count+1),
        
        return {
            'name': 'Create a new contract',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_model': 'hr.contract',
            'type': 'ir.actions.act_window',
            'context': "{{'default_employee_id': {},'default_name': {}}}".format(self.id,contract_name),
        }
    
    def new_benefit_pop_up(self):
        view_id = self.env.ref('vcls-hr.view_benefit_form').id
        return {
            'name': 'Create a new benefit set',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_model': 'hr.benefit',
            'type': 'ir.actions.act_window',
            'context': "{{'default_employee_id': {}}}".format(self.id),
        }