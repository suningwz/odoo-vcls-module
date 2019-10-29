# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    old_id = fields.Char(copy=False, readonly=True)

    @api.model
    def create_invoice_from_analytic_line(self):
        line_ids = self.env['account.analytic.line'].search([('stage_id', '=', 'invoiced'), ('old_id', '!=', False)])
        # Calculate data
        datas = {}
        for line_id in line_ids:
            sol_id = line_id.task_id.sale_line_id
            so_id = line_id.task_id.sale_order_id.parent_id or line_id.task_id.sale_order_id
            if so_id in datas:
                datas[so_id].append([sol_id, line_id.so_line_unit_price, line_id.unit_amount])
            else:
                datas.update({so_id: [[sol_id, line_id.so_line_unit_price, line_id.unit_amount]]})
        # Prepare invoices
        for order_id, line_ids in datas.items():
            for line_id in line_ids:
                values = {
                    'partner_id': order_id.partner_id.id,
                    'state': 'paid'
                }
                invoice = self.env['account.invoice'].create(values)
                vals = {
                    'product_id': line_id[0].product_id.id,
                    'price_unit': line_id[2],
                    'account_analytic_id': line_id[0].order_id.analytic_account_id.id,
                    'quantity': line_id[1],
                    'account_id': line_id[0].order_id.partner_id.property_account_receivable_id.id,
                    'name': line_id[0].product_id.name,
                    'sale_line_ids': [(6, 0, [line_id[0].id])],
                    'invoice_id': invoice.id,
                }
                self.env['account.invoice.line'].create(vals)
