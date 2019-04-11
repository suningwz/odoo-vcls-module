# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class ChangeRequest(models.Model):
    
    _inherit = 'helpdesk.ticket'
    _name = 'helpdesk.change.request'
    reason_for_change = fields.Text('Reason for Change')
    due_date = fields.Date(string="Due Date")
    impact = fields.Integer('10','30','50','70')
    severity = fields.Selection(string="Severity",[('1','Low / Informational'),('2','Normal / Minor'),('3','Significant / Critical')])
    main_risks = fields.Text('Main risks')
    priority = fields.Selection(string="Priority",[('1','Standard'),('2','Minor'),('3','Medium'),('4','Critical')])
    cmb_meeting_date = fields.Date(string="CMB Meeting date")
    validation_status = fields.Selection(string="Validation Status",[('1','Approved'),('2','Rejected'),('3','On Hold')])

    risk_analysis = fields.Many2one() 
    implementation_testing_plan = fields.Many2one()
    rollback_plan = fields.Many2one()
    backout_plan = fields.Many2one()




