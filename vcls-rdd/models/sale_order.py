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

    @api.multi
    def delete_empty_sections(self):
        for order in self:
            datas = {self.env['sale.order.line']: self.env['sale.order.line']}
            last_parent = self.env['sale.order.line']
            for line in order.order_line:
                if line.display_type != 'line_section':
                    datas[last_parent] += line
                else:
                    datas.update({line: self.env['sale.order.line']})
                    last_parent = line
            for key,vals in datas.items():
                if not vals and (key.name == 'Hourly Rates' or key.name == 'Subscriptions'):
                    self._cr.execute("DELETE FROM sale_order_line where id in %s", (tuple(key.ids),))
        return True

    @api.multi
    def delete_duplicate_hourly_rate_lines(self):
        for order in self:
            datas = {self.env['sale.order.line']: self.env['sale.order.line']}
            last_parent = self.env['sale.order.line']
            must_be_deleted = self.env['sale.order.line']
            for line in order.order_line:
                if line.display_type != 'line_section':
                    datas[last_parent] += line
                else:
                    datas.update({line: self.env['sale.order.line']})
                    last_parent = line
            grouped_data = {}
            named = {}
            for key, vals in datas.items():
                if vals and key.name == 'Hourly Rates':
                    for val in vals:
                        if val.product_id.id in grouped_data:
                            if grouped_data[val.product_id.id] < val.price_unit:
                                grouped_data[val.product_id.id] = val.price_unit
                                must_be_deleted += named[val.product_id.id]
                            else:
                                must_be_deleted += val
                        else:
                            grouped_data[val.product_id.id] = val.price_unit
                            named[val.product_id.id] = val
            if must_be_deleted:
                if len(must_be_deleted) > 1:
                    self._cr.execute("DELETE FROM sale_order_line where id in {}".format(tuple(must_be_deleted.ids)))
                else:
                    self._cr.execute("DELETE FROM sale_order_line where id = {}".format(must_be_deleted.id))
        return True

    @api.multi
    def _create_section(self, section):
        self.ensure_one()
        if section not in self.order_line.filtered(lambda l: l.display_type == 'line_section').mapped('name'):
            self.env['sale.order.line'].create({
                'display_type': 'line_section',
                'name': section,
                'order_id': self.id
            })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    old_id = fields.Char("Old Id", copy=False, readonly=True)
    milestone_date = fields.Date("Milestone date")
    mig_qty_invoiced = fields.Float(readonly=True)
    mig_qty_delivered = fields.Float(readonly=True)
    section_name = fields.Char()  # For migration only to remove after

    @api.multi
    def _get_ts_invoicing_mode(self, vals):
        if self.env.user.context_data_integration and vals.get('ts_invoicing_mode') \
                and not vals.get('display_type'):
            invoicing_mode = vals.get('ts_invoicing_mode')
            order = self.env['sale.order'].browse(vals.get('order_id'))
            if not order.ts_invoicing_mode:
                order.ts_invoicing_mode = invoicing_mode
                if vals.get('section_name'):
                    order._create_section(vals.get('section_name'))
                    del vals['section_name']
                vals['order_id'] = order.id
            elif order.ts_invoicing_mode != invoicing_mode:
                if order.child_ids:
                    if vals.get('section_name'):
                        order.child_ids[0]._create_section(vals.get('section_name'))
                        del vals['section_name']
                    vals['order_id'] = order.child_ids[0].id
                else:
                    new_order = order.copy({'ts_invoicing_mode': invoicing_mode,
                                            'parent_id': order.id,
                                            'order_line': []})
                    if vals.get('section_name'):
                        new_order._create_section(vals.get('section_name'))
                        del vals['section_name']
                    vals['order_id'] = new_order.id
            else:
                if order.child_ids:
                    if vals.get('section_name'):
                        order._create_section(vals.get('section_name'))
                        del vals['section_name']
                    vals['order_id'] = order.id
                else:
                    new_order = order.copy({'ts_invoicing_mode': invoicing_mode,
                                            'parent_id': order.id,
                                            'order_line': []})
                    if vals.get('section_name'):
                        new_order._create_section(vals.get('section_name'))
                        del vals['section_name']
                    vals['order_id'] = new_order.id
        return vals

    @api.model
    def create(self, vals):
        vals = self._get_ts_invoicing_mode(vals)
        return super(SaleOrderLine, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = self._get_ts_invoicing_mode(vals)
        return super(SaleOrderLine, self).write(vals)

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _get_invoice_qty(self):
        """
        Update qty_invoiced field with migrating value if mig_qty_invoiced is set
        """
        for line in self:
            qty_invoiced = line.mig_qty_invoiced
            if not qty_invoiced:
                for invoice_line in line.invoice_lines:
                    if invoice_line.invoice_id.state != 'cancel':
                        if invoice_line.invoice_id.type == 'out_invoice':
                            qty_invoiced += invoice_line.uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
                        elif invoice_line.invoice_id.type == 'out_refund':
                            qty_invoiced -= invoice_line.uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
            line.qty_invoiced = qty_invoiced
        super()._get_invoice_qty()

    @api.multi
    @api.depends('qty_delivered_method', 'qty_delivered_manual', 'analytic_line_ids.so_line', 'analytic_line_ids.unit_amount', 'analytic_line_ids.product_uom_id')
    def _compute_qty_delivered(self):
        """
        Update qty delivered with migrating value if mig_qty_delivered is set
        """
        if self.env.user.context_data_integration:
            lines_by_analytic = self.filtered(lambda sol: sol.qty_delivered_method == 'analytic')
            mapping = lines_by_analytic._get_delivered_quantity_by_analytic([('amount', '<=', 0.0)])
            for so_line in lines_by_analytic:
                so_line.qty_delivered = mapping.get(so_line.id, 0.0)
            # compute for manual lines
            for line in self:
                qty_delivered = line.mig_qty_delivered
                if not qty_delivered and line.qty_delivered_method == 'manual':
                    qty_delivered = line.qty_delivered_manual or 0.0
                line.qty_delivered = qty_delivered
        else:
            return super(SaleOrderLine, self)._compute_qty_delivered()
