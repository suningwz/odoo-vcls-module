# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class LeaveType(models.Model):
    
    _inherit = 'hr.leave.type'
    _order = 'sequence'
   
    #################
    # Custom Fields #
    #################
    
    impacts_lunch_tickets = fields.Boolean(
        string='Impact Lunch Ticket',)
    
    max_carry_over = fields.Integer(
        string='Maximum Carry Over',
        default='0',)
    
    comment = fields.Char(
        string='Comment',)
    
    is_managed_by_hr = fields.Boolean(
        string='Is Managed by HR',
        default='FALSE',)