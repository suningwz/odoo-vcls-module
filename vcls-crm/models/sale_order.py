# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):

    _inherit = 'sale.order'
