# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class RiskType(models.Model):

    _name = 'risk.type'
    _description = 'A Type of Risk'

    name = fields.Char(required = True)

    active = fields.Boolean(required = True)
    
    description = fields.Char()
    
    model_name = fields.Char(required = True)
    
    group_id = fields.Many2one('res.groups')

    notify = fields.Boolean()
    
    weight = fields.Integer(default = 1)
    
    category = fields.Char()

class Risk(models.Model):
    _name = 'risk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'A Risk'

    risk_type_id = fields.Many2one('risk.type',
                                    string = "Type of risk",
                                    required = True)

    note = fields.Char()

    resource = fields.Char(string='Resource', index=True, help="If not set, acts as a default value for new resources")

    risk_level = fields.Selection([(1, 'Low'), (2, 'Moderate'), (3, 'Significant'), (4, 'High')], 'Risk Level',)

    last_notification = fields.Datetime(readonly = True)

    score = fields.Integer(string = "Score", compute="_compute_score")

    @api.depends('risk_level', 'risk_type_id.weight')
    def _compute_score(self):
        for risk in self:
            if risk.risk_level:
                risk.score = risk.risk_level * risk.risk_type_id.weight
            else:
                risk.score = 0

    @api.model
    def _raise_risk(self, risk_type, resource):
        risk = self.env['risk'].create({'risk_type_id': risk_type.id, 'resource': resource})
        risk.send_notification()
        return risk

    def send_notification(self):
        risk_type = self.risk_type_id
        if risk_type.notify:
            partner_ids = []
            for user in risk_type.group_id.users:
                partner_ids.append(user.partner_id.id)
            self.message_subscribe(partner_ids=partner_ids)
            self.message_post(body="Risk created", partner_ids=[4, partner_ids])
            self.last_notification = datetime.datetime.now()

