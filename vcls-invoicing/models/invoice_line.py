# -*- coding: utf-8 -*-

from odoo import models, fields, api


import logging
_logger = logging.getLogger(__name__)


class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    section_line_id = fields.Many2one(
        'account.invoice.line',
        string='Line section',
        compute='_get_section_line_id',
        store=False
    )

    @api.multi
    def _get_section_line_id(self):
        for line in self:
            invoice_line_ids = line.invoice_id.invoice_line_ids
            current_section_line_id = False
            for invoice_line_id in invoice_line_ids:
                if invoice_line_id.display_type == 'line_section':
                    current_section_line_id = invoice_line_id
                elif line == invoice_line_id:
                    line.section_line_id = current_section_line_id
                    break

    @api.model
    def create(self, values):
        result = super(InvoiceLine, self).create(values)
        if result.purchase_line_id and not result.purchase_line_id.is_rebilled:
            result.account_analytic_id = False
        return result
