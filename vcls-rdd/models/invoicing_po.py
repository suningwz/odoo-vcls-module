# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class InvoicingPo(models.Model):
    _inherit = 'invoicing.po'

    order_date = fields.Date(string="Order Date")
    old_id = fields.Char("Old Id", copy=False, readonly=True)
    migrated_invoiced_amount = fields.Monetary(readonly=True)
    invoice_ids = fields.One2many('account.invoice', 'po_id', readonly=True)

    @api.multi
    def _compute_invoiced_amount(self):
        if self.env.user.context_data_integration:
            for record in self:
                invoiced_amount = record.migrated_invoiced_amount
                if not invoiced_amount:
                    invoiced_amount = sum([invoice.amount_untaxed for invoice in record.invoice_ids])
                record.invoiced_amount = invoiced_amount
        else:
            super(InvoicingPo,self)._compute_invoiced_amount()
