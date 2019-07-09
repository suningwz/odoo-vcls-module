# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class InvoicingPO(models.Model):
    _name = 'invoicing.po'
    _description = 'Client Purchase Order'
    
    name = fields.Char()

    active = fields.Boolean(default = True)

    client_ref = fields.Char()

    partner_id = fields.Many2one('res.partner')

    amount = fields.Monetary()

    currency_id = fields.Many2one('res.currency', 
                                    related = 'partner_id.default_currency_id')

    invoiced_amount = fields.Monetary(compute='_compute_invoiced_amount')

    @api.one
    def _compute_invoiced_amount(self):
        self.invoiced_amount = sum(invoice.amount_untaxed for invoice in self.env['account.invoice'].search([('po_id','=',self.id)]))
        