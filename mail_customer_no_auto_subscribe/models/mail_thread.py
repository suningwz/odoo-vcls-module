# -*- coding: utf-8 -*-
from odoo import models, fields, api, http
from odoo.osv import expression


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, customer_ids=None):
        model_definition = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
        if partner_ids and not self._context.get('allow_auto_follow') and \
                model_definition and \
                (not model_definition.allow_customer_follow or
                 not model_definition.allow_supplier_follow):
            domain = []
            if not model_definition.allow_customer_follow:
                domain = expression.OR([
                    domain, [('customer', '=', True)]
                ])
            if not model_definition.allow_supplier_follow:
                domain = expression.OR([
                    domain, [('supplier', '=', True)]
                ])
            domain = expression.AND([
                domain, [('id', 'in', partner_ids)]
            ])
            not_allowed_partner_ids = self.env['res.partner'].sudo().search(domain).ids
            if not_allowed_partner_ids:
                partner_ids = [pid for pid in partner_ids if pid not in not_allowed_partner_ids]
        return super(MailThread, self)._message_subscribe(
            partner_ids, channel_ids,
            subtype_ids, customer_ids
        )
