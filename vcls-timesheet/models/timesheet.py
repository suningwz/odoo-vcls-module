from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError


class TimesheetAdjustment(models.Model):
    _name = 'timesheet.adjustment.reason'

    name = fields.Char()
    active = fields.Boolean()