# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    old_id = fields.Char()

    @api.model
    def get_alpha_index(self, index):
        return 'SF'

    @api.model
    def create(self, vals):
        print(vals.get('company_id'))
        return super(SaleOrder, self).create(vals)