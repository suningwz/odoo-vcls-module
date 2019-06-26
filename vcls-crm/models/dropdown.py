# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TherapeuticArea(models.Model):

    _name = 'therapeutic.area'
    _description = "Segment leads by therapeutic area"

    active = fields.Boolean(
        default = True,
    )
    
    name = fields.Char(
        required = True,
    )
    
