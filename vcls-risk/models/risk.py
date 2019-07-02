# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class RiskType(models.Model):

    _name = 'risk.type'
    _description = 'A Type of Risk'

    name = fields.Char(required = True)

    active = fields.Boolean(required = True)
    
    description = fields.Char()
    
    model_name = fields.Char(required = True)
    
    group_id = fields.Many2one('res.groups')

    notify = fields.Boolean()
    
    weight = fields.Integer(default = 1)
    
    category = fields.Char()
