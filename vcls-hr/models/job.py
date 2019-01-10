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
    
    support_fct = fields.Char(
        string='Support Function',)
    
    #job segmentation used to manage access rights in other systems (as IT process).
    
    project_fct_id = fields.Many2one(
        'hr.project_business_fct',)
    
    
    vcls_activity_id = fields.Many2one(
        'hr.vcls_activities',)
    
    project_role_id = fields.Many2one(
        'hr.project_role',)
    
    view_mode = fields.Selection([
        ('operation', 'Operation'),
        ('support', 'Support'),
        ('undef','Undefined')], 
        compute='_get_view_mode',
        store=False,)
    
    #######################
    # Calculation Methods #
    #######################
    
    @api.depends('department_id','support_fct','vcls_activity_id','project_role_id')
    def _compute_name(self):
        for rec in self:
            if rec.department_id.id == self.env.ref('vcls-hr.department_operations').id:
                if rec.vcls_activity_id:
                    rec.name = "{} - ".format(rec.vcls_activity_id.name)
                if rec.project_role_id:
                    rec.name = "{}{}".format(rec.name,rec.project_role_id.name)
            else:
                if rec.department_id:
                    rec.name = "{} - ".format(rec.department_id.name)
                if rec.support_fct:
                    rec.name = "{}{}".format(rec.name,rec.support_fct)
                    
    @api.depends('department_id')
    def _get_view_mode(self):
        for rec in self:
            if rec.department_id.id == self.env.ref('vcls-hr.department_operations').id:
                rec.view_mode = 'operation'
            elif rec.department_id.id:
                rec.view_mode = 'support'
            else:
                rec.view_mode = 'undef'
    
    #######################
    # Constrains Methods #
    #######################
    
    @api.constrains('billable_target_percentage')
    def _check_target_percentage(self):
        for rec in self:
            if not (0<=rec.billable_target_percentage<=1.0): #configured value can't be above 1
                raise ValidationError("The Billable Target Percentage is out of the valid range (0% to 100%)")