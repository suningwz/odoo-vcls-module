# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
