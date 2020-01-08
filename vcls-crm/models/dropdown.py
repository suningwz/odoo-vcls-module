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
 
 
class TargetedIndication(models.Model):

    _name = 'targeted.indication'
    _description = "Segment leads by targeted indication"

    active = fields.Boolean(
        default = True,
    )
    
    name = fields.Char(
        required = True,
    ) 

    therapeutic_area_id = fields.Many2one(
        comodel_name = 'therapeutic.area',
        required = True,
    )
    

class StageDevelopment(models.Model):

    _name = 'stage.development'
    _description = "Segment leads by Stage of development"

    active = fields.Boolean(
        default = True,
    )
    
    name = fields.Char(
        required = True,
    )  
