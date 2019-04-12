# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class ChangeRequest(models.Model):
    _name = 'helpdesk.change.request'
    _inherit = 'helpdesk.ticket'
    reason_for_change = fields.Text('Reason for Change')
    due_date = fields.Date(string="Due Date")
    impact = fields.Integer()
    severity = fields.Selection([('1','Low / Informational'),('2','Normal / Minor'),('3','Significant / Critical')],string="Severity")
    main_risks = fields.Text('Main risks')
    priority = fields.Selection([('1','Standard'),('2','Minor'),('3','Medium'),('4','Critical')],string="Priority")
    cmb_meeting_date = fields.Date(string="CMB Meeting date")
    validation_status = fields.Selection([('1','Approved'),('2','Rejected'),('3','On Hold')],string="Validation Status")
    risk_analysis = fields.Many2one() 
    implementation_testing_plan = fields.Many2one()
    rollback_plan = fields.Many2one()
    backout_plan = fields.Many2one() 




