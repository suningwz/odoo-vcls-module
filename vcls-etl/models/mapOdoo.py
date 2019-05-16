from odoo import models, fields, api

class mapOdoo(models.Model):
    _name = 'map.odoo'
    odModelName = fields.Char()
    externalName = fields.Char()
    externalOdooId = fields.Char()
    odooId = fields.Char()
    stage = fields.Selection([
        (1, 'New'),
        (2, 'Verified')],
        string='Stage',
        track_visibility='onchange',
        default=1,
    )
    #toReviewed = fields.Selection()