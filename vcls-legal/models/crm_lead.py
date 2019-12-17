from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    agreement_count = fields.Integer(compute='_compute_agreement_count')

    agreement_id = fields.Many2one(
        'agreement',
        string='Related Agreement',
        domain="['|',('partner_id','=',partner_id),('partner_id.parent_id','=',partner_id)]",
    )

    def _compute_agreement_count(self):
        """Compute the number of distinct subscriptions linked to the order."""
        for lead in self:
            lead_count = len(self.env['agreement'].read_group([('partner_id', '=', lead.partner_id.id)],
                                                    ['code'], ['code']))
            lead.agreement_count = lead_count

    def action_open_agreement(self):
        """Display the linked agreement and adapt the view to the number of records to display."""
        self.ensure_one()
        agreements = self.partner_id.mapped('agreement_ids')
        action = self.env.ref('agreement_legal.agreement_operations_agreement').read()[0]
        if len(agreements) > 1:
            action['domain'] += [('id', 'in', agreements.ids)]
        elif len(agreements) == 1:
            action['views'] = [(self.env.ref('agreement_legal.partner_agreement_form_view').id, 'form')]
            action['res_id'] = agreements.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
