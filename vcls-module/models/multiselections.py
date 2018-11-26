# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class Diploma(models.Model):
    
    _name = 'hr.diploma'
    _description = 'Diplomas'
    
    name = fields.Char(
        required=True,)

    """ COVERED BY DEPARTMENT OBJECT >> TO DELETE """
class VclsBusinessFct(models.Model):
    _name = 'hr.vcls_business_fct'
    _description = 'Business Functions'
    
    name = fields.Char(
        required=True,)
    
    short = fields.Char(
        required=True,)    

class ProjectBusinessFct(models.Model):
    _name = 'hr.project_business_fct'
    _description = 'Project Functions'
    
    name = fields.Char(
        required=True,)
    short = fields.Char(
        required=True,)

class ProjectRole(models.Model):
    _name = 'hr.project_role'
    _description = 'Project Roles'
    
    name = fields.Char(
        required=True,)

class VclsActivities(models.Model):
    _name = 'hr.vcls_activities'
    _description = 'VCLS Activities'
    
    name = fields.Char(
        required=True,)
    head_id = fields.Many2one(
        'hr.employee',
        string='Head',)

class BenefitType(models.Model):
    _name = 'hr.benefit_type'
    _description = 'Type of Benefits'
    
    # Custom Fields 
    name = fields.Char(
        required=True,)
    
    recurrence = fields.Selection(
        selection='_selection_recurrence',)
    
    @api.model
    def _selection_recurrence(self):
        return [
            ('monthly','Monthly'),
            ('yearly','Yearly'),
        ]
