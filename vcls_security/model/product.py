# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'


class Product(models.Model):
    _inherit = 'product.product'

