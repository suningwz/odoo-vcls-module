# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class Contact(models.Model):
    _inherit = 'res.partner'
    risk_ids = fields.Many2many('risk', string='Risk')

    def action_risk(self):
        view_id = self.env.ref('vcls-risk.view_risk_tree').id
        risk_ids = self.risk_ids

        print(risk_ids)
        return {
            'name': 'All Risks',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view_id,
            'target': 'current',
            'res_model': 'risk',
            'type': 'ir.actions.act_window',
            'context': {'search_default_id': risk_ids.ids,},
        } 