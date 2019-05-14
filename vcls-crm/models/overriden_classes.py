# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class CoutryGroup(models.Model):

    _inherit = 'res.country.group'
    
    default_am = fields.Many2one(
        'res.users',
        string = "Default Account Manager",
        domain = "[('employee','=',True)]",
    )