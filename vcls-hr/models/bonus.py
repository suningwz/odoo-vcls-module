# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models
import xlrd

class bonus(models.Model):
    
    _name = 'hr.bonus'
    _description = 'Employee Bonus'
    _order = 'date desc'
    
    #################
    # Custom Fields #
    #################
    
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,)
    
    currency_id = fields.Many2one(
        related = 'employee_id.company_id.currency_id',
        string="Currency",
        readonly=True,)
    
    amount = fields.Monetary(
        string="Amount",
        required="True",)
    
    date = fields.Date(
        string="Allocation Date",
        required="True",)
    
    comment = fields.Text(
        string="Comment",)
    
    bonus_type = fields.Selection(
        string = 'Type',
        selection = [
            ('performance','Annual Performance Bonus'),
            ('cooptation','Cooptation Bonus'),
            ('welcome','Welcome Bonus'),
            ('other','Other Bonus'),
        ]
    )