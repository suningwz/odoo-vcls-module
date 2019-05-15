from odoo import models, fields, api

class mapOdoo(models.Model):
    _name = 'map.odoo'
    odModelName = fields.Char()
    externalName = fields.Char()
    externalOdooId = fields.Char()
    odooId = fields.Char()
    #toReviewed = fields.Selection()