# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    old_id = fields.Char(copy=False, readonly=True)
