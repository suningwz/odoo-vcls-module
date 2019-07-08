from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'
    
    communication_elligible = fields.Boolean('Communication Elligible', help='Indicate if product is elligible to the communication rate or not')
