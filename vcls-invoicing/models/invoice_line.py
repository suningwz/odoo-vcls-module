# -*- coding: utf-8 -*-

from odoo import models, fields, api


import logging
_logger = logging.getLogger(__name__)


class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, values):
        result = super(InvoiceLine, self).create(values)
        if result.purchase_line_id and not result.purchase_line_id.is_rebilled:
            result.account_analytic_id = False
        return result
