from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'
    
    communication_rate = fields.Float('Communication rate')
