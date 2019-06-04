# -*- coding: utf-8 -*-

from odoo import api, fields, models

# Basic copy of crm.lost.reason
class LostReason(models.Model):
    _name = "crm.won.reason"
    _description = 'Opp. Won Reason'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)


# Basic copy of crm.lead.lost
class CrmLeadWon(models.TransientModel):
    _name = 'crm.lead.won'
    _description = 'Get Won Reason'

    won_reason_id = fields.Many2one('crm.won.reason', 'Won Reason')

    @api.multi
    def action_won_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        leads.write({'won_reason': self.won_reason_id.id})
        return leads.action_set_won()
