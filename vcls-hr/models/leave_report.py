# -*- coding: utf-8 -*-

#Python Imports
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

class LeaveReport(models.Model):
    _inherit = 'hr.leave.report'
    
   
    #################
    # Custom Fields #
    #################
    
    lm_user_id = fields.Many2one(
        'res.users',
        related='employee_id.parent_id.user_id',)