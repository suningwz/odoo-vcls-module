# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CoreTeam(models.Model):
    _inherit = 'core.team'

    old_id = fields.Char(copy=False, readonly=True)

    @api.multi
    def write(self, vals):
        if isinstance(vals.get('consultant_ids'), int) and \
                self.env.user.context_data_integration:
            vals['consultant_ids'] = [(4, vals['consultant_ids'])]
        return super(CoreTeam, self).write(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    old_id = fields.Char("Old Id", copy=False, readonly=True)

    @api.model
    def get_alpha_index(self, index):
        if not self.env.user.context_data_integration:
            return super(SaleOrder, self).get_alpha_index(index)
        return 'SF'

    @api.multi
    def create_invoice_from_analytic_line(self):
        for order in self:
            if not self.env['account.invoice'].search([('origin', '=', order.name)]):
                parent_project, child_projects = order._get_family_projects()
                family_projects = (parent_project | child_projects)
                line_ids = self.env['account.analytic.line'].search(
                    [('stage_id', '=', 'invoiced'), ('old_id', '!=', False),
                     ('project_id', 'in', family_projects.ids)])
                if line_ids:
                    invoice_vals = {'partner_id': order.partner_id.id,
                                    'origin': order.name,
                                    'po_id': order.po_id.id,
                                    'type': 'out_invoice',
                                    'account_id': order.partner_invoice_id.property_account_receivable_id.id,
                                    'state': 'paid'}
                    ail_vals = []
                    for line in line_ids:
                        task = line.task_id
                        vals = (0, 0, {
                            'product_id': task.sale_line_id.product_id.id,
                            'price_unit': line.so_line_unit_price,
                            'account_analytic_id': task.sale_line_id.order_id.analytic_account_id.id,
                            'quantity': line.unit_amount,
                            'account_id': task.sale_line_id.order_id.partner_id.property_account_receivable_id.id,
                            'name': task.sale_line_id.product_id.name,
                            'sale_line_ids': [(6, 0, [task.sale_line_id.id])]})
                        ail_vals.append(vals)
                    invoice_vals['invoice_line_ids'] = ail_vals
                    invoice_id = self.env['account.invoice'].sudo().create(invoice_vals)
                    order.invoice_ids = [invoice_id.id]
        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    old_id = fields.Char("Old Id", copy=False, readonly=True)
    milestone_date = fields.Date("Milestone date")

    @api.model
    def create(self, vals):
        if self.env.user.context_data_integration and vals.get('ts_invoicing_mode') \
                and not vals.get('display_type'):
            invoicing_mode = vals.get('ts_invoicing_mode')
            order = self.env['sale.order'].browse(vals.get('order_id'))
            if not order.ts_invoicing_mode:
                order.ts_invoicing_mode = invoicing_mode
            elif order.ts_invoicing_mode != invoicing_mode:
                if order.child_ids:
                    vals['order_id'] = order.child_ids[0].id
                else:
                    new_order = order.copy({'ts_invoicing_mode': invoicing_mode,
                                            'parent_id': order.id,
                                            'order_line': []})
                    vals['order_id'] = new_order.id
        return super(SaleOrderLine, self).create(vals)
