from odoo import models, fields, api

class mapOdoo(models.Model):
    _name = 'map.odoo'
    _description = 'used to map external values to Odoo Ids'

    odModelName = fields.Char()
    externalName = fields.Char()
    externalOdooId = fields.Char()
    odooId = fields.Char()
    #toReviewed = fields.Selection()