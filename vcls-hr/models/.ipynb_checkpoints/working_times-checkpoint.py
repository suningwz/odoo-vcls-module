# -*- coding: utf-8 -*-

#Python Imports
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models

class WorkingTimes(models.Model):
    
    _inherit = 'resource.calendar'
    
    #Custom fields
    effective_percentage = fields.Float(
        default = 1.0,
        string='Effective Percentage')
    
    weekly_hours = fields.Float(
        default=40.0,
        string='Standard hours per week')
    
    effective_hours = fields.Float(
        default=40.0,
        string='Effective hours per week')
    
    #Overriden fields