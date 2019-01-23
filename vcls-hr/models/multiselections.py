# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class Diploma(models.Model):
    
    _name = 'hr.diploma'
    _description = 'Diplomas'
    
    name = fields.Char(
        required=True,)

# A list of business functions to be used for permission management as well as segmentation of the employee
class BusinessFct(models.Model):
    _name = 'hr.project_business_fct'
    _description = 'Business Functions'
    
    name = fields.Char(
        required=True,)
    short = fields.Char(
        required=True,)

#The list of role will be used on invoices, this is the client oriented side of our internal organisation
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

class Office(models.Model):
    
    _name = 'hr.office'
    _description = 'VCLS Office'
    
    name = fields.Char()
    
'''
class WorkPermit(models.Model):
    _name = 'hr.work_permit'
    
    name = fields.Char()
    company_id = 
'''

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