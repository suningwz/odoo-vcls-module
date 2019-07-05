# -*- coding: utf-8 -*-

#Python Imports
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class Employee(models.Model):
    
    _inherit = 'hr.employee'

    employee_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ('template', 'Template'),
        ],default = 'internal'
    )

    