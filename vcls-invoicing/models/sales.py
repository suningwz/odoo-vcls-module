# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class SalesOrder(models.Model):
    _inherit = 'sale.order'

    po_id = fields.Many2one('invoicing.po', string ='Purchase Order')