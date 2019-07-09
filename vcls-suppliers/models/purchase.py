# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    expertise_id = fields.Many2one(
        'expertise.area',
        string="Area of Expertise",
    )