from odoo import api,fields, models


class Contact(models.Model):
    _inherit = "res.partner"
    agre_count = fields.Integer(compute='_compute_agre_count')

    @api.depends('agreement_ids')
    def _compute_agre_count(self):
        self.agre_count = len(self.agreement_ids)


    def action_agre(self):
        agre_ids = self.env['agreement'].search([('partner_id','=',self.id)]).ids

        return {
            'name': 'Agreement',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'agreement',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', agre_ids)], 
            'context': {"default_partner_id": self.id},
        } 