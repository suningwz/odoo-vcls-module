from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class Product(models.Model):
    _inherit = 'product.template'

    time_category_ids = fields.Many2many(
        'project.time_category',
        string='Default Time Categories',
        )