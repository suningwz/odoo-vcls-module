# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class bonus(models.Model):
    
    _name = 'hr.bonus'
    _description = 'Employee Bonus'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char()
    
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required="True",)
    
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required="True",)
    
    amount = fields.Monetary(
        string="Amount",
        required="True",)
    
    date = fields.Date(
        string="Allocation Date",
        required="True",)
    
    comment = fields.Text(
        string="Comment",)