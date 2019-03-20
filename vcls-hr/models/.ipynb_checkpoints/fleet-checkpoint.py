# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class Contract(models.Model):
    
    _inherit = 'fleet.vehicle'
    
   
    #################
    # Custom Fields #
    #################
    
    info = fields.Char(
        compute='_get_info',)
    
    @api.depends('model_id','license_plate')
    def _get_info(self):
        for car in self:
            car.info = "{}/{} ({})".format(car.model_id.brand_id.name,car.model_id.name,car.license_plate)