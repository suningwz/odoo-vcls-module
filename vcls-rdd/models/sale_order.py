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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    old_id = fields.Char("Old Id", copy=False, readonly=True)

    @api.model
    def create(self, vals):
        if self.env.user.context_data_integration:
            invoicing_mode = vals.get('ts_invoicing_mode')
            order = self.env['sale.order'].browse(vals.get('order_id'))
            if not order.ts_invoicing_mode:
                order.ts_invoicing_mode = invoicing_mode
            elif order.ts_invoicing_mode == invoicing_mode:
                pass
            else:
                if order.child_ids:
                    vals['order_id'] = order.child_ids[0].id
                else:
                    new_order = order.copy({'ts_invoicing_mode': invoicing_mode, 'parent_id': order.id})
                    vals['order_id'] = new_order.id
        return super(SaleOrderLine, self).create(vals)
