# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class ChangeRequest(models.Model):
    
    _inherit = 'helpdesk.ticket'
    _name = 'helpdesk.change.request'
    reason_for_change = fields.Text('Reason for Change')
    due_date = fields.Date()
    impact = fields.Integer('10','30','50','70')
    severity = fields.Selection([('Low','Informational'),('Normal','Minor'),('Significant','Critical')])
    main_risks = fields.Text()
    priority = fields.Selection()
    cmb_meeting_date = fields.Date()
    validation_status = fields.Selection()




