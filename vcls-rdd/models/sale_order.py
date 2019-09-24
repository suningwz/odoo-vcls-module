# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    old_id = fields.Char(copy=False, readonly=True)

    @api.model
    def get_alpha_index(self, index):
        return 'SF'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    old_id = fields.Char(copy=False, readonly=True)