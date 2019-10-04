# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CoreTeam(models.Model):
    _inherit = 'core.team'

    old_id = fields.Char(copy=False, readonly=True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    old_id = fields.Char(copy=False, readonly=True)

    @api.model
    def get_alpha_index(self, index):
        if not self.env.user.context_data_integration:
            return super(SaleOrder, self).get_alpha_index(index)
        return 'SF'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    old_id = fields.Char(copy=False, readonly=True)

    # @api.model
    # def create(self, vals):
    #     if self.env.user.context_data_integration:
    #         order = self.env['sale.order'].browse(vals.get('order_id'))
    #         if not order.ts_invoicing_mode:
    #             order.ts_invoicing_mode = vals.get('ts_invoicing_mode')
    #     return super(SaleOrderLine, self).create(vals)
