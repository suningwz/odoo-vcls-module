from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class TimeCategory(models.Model):
    _name = 'project.time_category'

    _description = 'Time Category'

    name = fields.Char()
    active = fields.Boolean(default="True")