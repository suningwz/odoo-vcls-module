# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models


class ExceptionalLeaveCategory(models.Model):
    
    _name = 'hr.exceptional.leave.category'
    _description = 'Exceptional Leave Category'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char(
        string='Category Name',)
    
    leave_type_id = fields.Many2one(
        'hr.leave.type',
        string='Related Leave Type',)
    
    company = fields.Char(
        related='leave_type_id.company_id.name',)
    
    default_max_allocated_days = fields.Float(
        string='Default Allocated Days',)
    
class ExceptionalLeaveCase(models.Model):
    
    _name = 'hr.exceptional.leave.case'
    _description = 'Exceptional Leave Cases'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char(
        string='Case',)
    
    category_id = fields.Many2one(
        'hr.exceptional.leave.category',
        string='Related Category',)
    
    max_allocated_days = fields.Float(
        string='Allocated Days',)