from odoo import fields, models


class Contact(models.Model):
    _inherit = "res.partner"

    def action_agre(self):
        agre_ids = self.env['agreement'].search([('partner_id','=',self.id)]).ids

        return {
            'name': 'Agreement',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'agreement',
            'type': 'ir.actions.act_window',
            'context': {'search_default_id': agre_ids},
        } 