# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class LeadSources(models.Model):

    _name = 'lead.source'

    active = fields.Boolean(
        default = True,
    )
    
    name = fields.Char(
        required = True,
    )