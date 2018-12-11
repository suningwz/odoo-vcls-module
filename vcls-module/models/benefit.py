# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class Benefit(models.Model):
    
    _name = 'hr.benefit'
    _description = 'Benefits'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char()
    
    '''
    employee_id = fields.Many2one(
        'hr.employee', 
        string="Employee", 
        required="True",)
    '''
    
    contract_id = fields.Many2one(
        'hr.contract',)
    
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required="True",)
    
    amount = fields.Monetary(
        string="Amount",
        required="True",)
    
    start_date = fields.Date(
        string="Start Date",
        required="True",)
    
    end_date = fields.Date(
        string="End Date",)
    
    comment = fields.Text(
        string="Comment",)
    
    recurrence = fields.Selection(
        selection='_selection_recurrence',)
    
    type = fields.Selection(
        selection='_selection_type',
        required="True",)
    
    #####################
    # Selection Methods #
    #####################
    
    @api.model
    def _selection_type(self):
        return [
            ('car','Car'),
            ('public_transport','Public Transport'),
            ('phone','Phone'),
        ]
    
    @api.model
    def _selection_recurrence(self):
        return [
            ('monthly','Monthly'),
            ('yearly','Yearly'),
        ]