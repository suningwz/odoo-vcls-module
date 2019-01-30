# -*- coding: utf-8 -*-

#Python Imports

#Odoo Imports
from odoo import api, fields, models

# Need record rules
class EmployeeConfidential(models.Model):
    # SPECIFIC CLASS ATTRIBUTES #
    _name = 'hr.employee.confidential'
    _description = 'Model used to store sensitive information about employee'
    
    _sql_constraints = [
                     ('employee_id_unique', 
                      'unique(employee_id)',
                      'Employee ID from EmployeeConfidential is not unique.')
                    ]
    
    # Relations with employee
    employee_id = fields.Many2one('hr.employee','employee', required=True) # add unique constraint
    # END OF SPECIFIC CLASS ATTRIBUTES #
    
    # CONFIDENTIAL PERSONAL INFORMATIONS #
    ## Administrative informations
    family_name_at_birth = fields.Char(
        String='Family Name at Birth',
        track_visibility='always',)
    
    birthday = fields.Date(String='Date of Birth')
    
    ssnid = fields.Char(String='Social Security Number')
    
    country_id = fields.Many2one(
        'res.country', String = 'Primary Citizenship')
    
    country2_id = fields.Many2one(
        'res.country', String = 'Secondary Citizenship')
    
    permit_no = fields.Char(String = 'Work Permit')
    work_permit_expire = fields.Date(String = 'Work Permit Expiring Date')
    
    link_employee_folder = fields.Char(
        string='Employee Folder',
        help='Paste folder url',
        track_visibility='always',)
    
    # Contact Informations
    
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
        'res.country', String = "Country")
    
    # Redefine object here instead of using another model
    # Previously related to address_home_id.email
    private_email = fields.Char(
        String="Private Email",)
    
    # Redefine object here instead of using another model
    
    private_phone = fields.Char(
        string='Private Phone')
    
    emergency_contact = fields.Char(String = 'Emergency Contact')
    emergency_phone = fields.Char(String = 'Emergency Phone')
    
    # Selection field in employee
    ice_contact_relationship = fields.Char(
        string='Emergency Contact Relationship')
    
    notes = fields.Text() # Don't have label
    
    # END OF CONFIDENTIAL PERSONAL INFORMATION #
    
    # CONFIDENTIAL JOB INFORMATION #
    ## Declare here sensitive attributes about the employee's job
    # END OF CONFIDENTIAL JOB INFORMATION #
    
    # CONFIDENTIAL TRIAL PERIOD INFORMATION #
    ### NOT HANDELD IN employee_confidential
    #### domain="[('company_id', '=', company_id)]" in employee
    '''
    trial_period_id = fields.Many2one(
        'hr.trial.period',
        string='Trial Period')
    
    trial_start_date = fields.Date(
        string='Trial Period Start Date',)

    trial_end_date = fields.Date(
        string='Trial Period End Date',
        compute='_compute_trial_end_date',)
    
    trial_notification_date = fields.Date(
        string='Trial Period Notification Date',
        compute='_compute_trial_end_date',)
    '''
    # END OF CONFIDENTIAL TRIAL PERIOD INFORMATION #
    
    # CONFIDENTIAL HEALTH CARE INFORMATION #
    
    last_medical_checkup = fields.Date(
        string="Last Medical Check-up",
        track_visibility='always',)
    
    specific_next_medical_checkup = fields.Date() #used to store manually entered value in the below inverse case
    
    next_medical_checkup = fields.Date(
        string="Next Medical Check-up",
        compute='_get_next_medical_checkup',
        # inverse='_set_next_medical_checkup',
        track_visibility='always',)
    
    need_specific_medical = fields.Boolean(
        string="Need Specific Medical Follow-up",
        track_visibility='always',)
    
    ## Health Insurance
    affiliated_company = fields.Char(String = 'Affiliated Company')
    affiliation_date = fields.Date(String = 'Affiliation Date')
    medical_policy_number = fields.Char(String = 'Medical Policy Number')
    # END OF CONFIDENTIAL HEALTH CARE INFORMATION #
    
    # CONFIDENTIAL TECHNICAL FIELDS #
    ## Declare here sensitive attributes of the technical fields
    # END OF CONFIDENTIAL TECHNICAL FIELDS #
    
    
    #################################
    # Automated Calculation Methods #
    #################################
    
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
            
    