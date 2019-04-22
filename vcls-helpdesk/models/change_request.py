# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class ChangeRequest(models.Model):
    _name = 'helpdesk.change.request'
    _description = 'Change Request'
    _inherit = 'helpdesk.ticket'

    name = fields.Char()
    reason_for_change = fields.Text('Reason for Change')
    due_date = fields.Date(string="Due Date")
    impact = fields.Selection([('0.1','10 %'),('0.3','30 %'),('0.5','50 %'),('0.7','70 %')],string="Impact")
    severity = fields.Selection([('1','Low / Informational'),('2','Normal / Minor'),('3','Significant / Critical')],string="Severity")
    main_risks = fields.Text('Main risks')
    priority = fields.Selection([('0','Standard'),('1','Minor'),('2','Medium'),('3','Critical')],string="Priority")
    cmb_meeting_date = fields.Date(string="CMB Meeting date")
    validation_status = fields.Selection([('1','Approved'),('2','Rejected'),('3','On Hold')],string="Validation Status")
    risk_analysis = fields.Char() 
    implementation_testing_plan = fields.Char()
    rollback_plan = fields.Char()
    backout_plan = fields.Char() 




