# -*- coding: utf-8 -*-

#Python Imports
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models

class TrialPeriod(models.Model):
    
    _name = 'hr.trial.period'
    _description = 'Trial Period'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char(
        compute='_compute_name',)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',)
    
    contract_type = fields.Selection(
        string='Contract Type',
        help='For french companies only',
        selection='_selection_contract',)
    
    duration = fields.Integer(
        string='Duration in Months',)
    
    notification_delay = fields.Integer(
        string='Notification Delay in days',)
    
    is_prolonged = fields.Boolean(
        string='Is Prolonged Period',)
    
    #################################
    # Automated Calculation Methods #
    #################################

    #Buid the name based on the company, type and prologation
    @api.depends('company_id','contract_type','is_prolonged')
    def _compute_name(self):
        for rec in self:
            rec.name = "{}".format(rec.company_id.name)
            if rec.contract_type:
                rec.name = "{} ({})".format(rec.name,rec.contract_type)
            if rec.is_prolonged:
                rec.name = "{} - PROLONGED".format(rec.name)
            rec.name = "{} - {} months".format(rec.name,rec.duration)
                
    @api.model
    def _selection_contract(self):
        return [
            ('ETAM','ETAM'),
            ('Cadre','Cadre'),
        ]