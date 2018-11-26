# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class Job(models.Model):
    
    _inherit = 'hr.job'
    
    ####################
    # Overriden Fields #
    ####################
    
    #in oder to enforce naming convention
    name = fields.Char(
        compute='_compute_name',)
      
    #################
    # Custom Fields #
    #################
    
    #job_percentage = fields.Float(string='Working Percentage')
    billable_target_percentage = fields.Float(
        string='Billable Target Percentage',)
    
    #job segmentation used to manage access rights in other systems (as IT process).
    project_fct_id = fields.Many2one(
        'hr.project_business_fct',)
    
    vcls_activity_id = fields.Many2one(
        'hr.vcls_activities',)
    
    project_role_id = fields.Many2one(
        'hr.project_role',)
    
    #######################
    # Calculation Methods #
    #######################
    
    @api.depends('vcls_activity_id','project_role_id','project_fct_id')
    def _compute_name(self):
        for rec in self:
            if rec.project_fct_id.name != None: #if a project fct is defined
                if rec.project_fct_id.name == 'Expert' : 
                    rec.name= '{} - {}'.format(rec.project_role_id.name, rec.vcls_activity_id.name) #for an Expert, we add the role to the name
                else: rec.name= '{}'.format(rec.project_fct_id.name)
    
    #######################
    # Constrains Methods #
    #######################
    
    @api.constrains('billable_target_percentage')
    def _check_target_percentage(self):
        for rec in self:
            if not (0<=rec.billable_target_percentage<=1.0): #configured value can't be above 1
                raise ValidationError("The Billable Target Percentage is out of the valid range (0% to 100%)")