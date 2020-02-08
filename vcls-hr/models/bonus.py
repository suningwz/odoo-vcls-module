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
        comodel_name='res.currency',
        related=False,
        string="Currency",
        default=lambda self: self.employee_id.company_id.currency_id,
    )
    
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

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if not self.currency_id:
            self.currency_id = self.employee_id.company_id.currency_id
