# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression

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
    
    @api.model
    def _timesheet_domain_get_invoiced_lines(self, sale_line_delivery):
        """
         We extend the domain to take in account the timesheet_limit date 
         as well as the vcls status of the timesheets.
         Take care to be aligned with the domain used to compute timesheet_ids at the sale.order model.
        """
        domain = super(InvoiceLine, self)._timesheet_domain_get_invoiced_lines(sale_line_delivery)
        #we get any of the timesheet limit dates of the so (all have to be the same)
        limit_date = None

        for line in sale_line_delivery:
            if line.order_id.timesheet_limit_date:
                limit_date = line.order_id.timesheet_limit_date
                break
        if limit_date:
            domain = expression.AND([domain, [('date', '<=', limit_date)]])
        domain = expression.AND([domain, [('stage_id', '=', 'invoiceable')]])
        #_logger.info("TS DOMAIN {}".format(domain))
        return domain