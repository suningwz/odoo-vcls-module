# -*- coding: utf-8 -*-
from odoo import models, fields


class IrModel(models.Model):
    _inherit = 'ir.model'

    allow_customer_follow = fields.Boolean(
        'Allow customers',
        default=False
    )
    allow_supplier_follow = fields.Boolean(
        'Allow suppliers',
        default=True
    )
