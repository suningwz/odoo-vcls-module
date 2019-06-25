from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError


class TimesheetAdjustment(models.Model):
    _name = 'timesheet.adjustment.reason'
    _description = 'Timesheet Adjustment Reason'

    name = fields.Char()
    active = fields.Boolean()