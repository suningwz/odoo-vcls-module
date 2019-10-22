# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class InvoicingPo(models.Model):
    _inherit = 'invoicing.po'

    order_date = fields.Date(string="Order Date")
