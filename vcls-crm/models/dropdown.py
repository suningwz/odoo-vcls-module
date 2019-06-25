# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TherapeuticArea(models.Model):

    _name = 'therapeutic.area'
    _description = "Used to segment leads according to their therapeutic area"

    active = fields.Boolean(
        default = True,
    )
    
    name = fields.Char(
        required = True,
    )
    