# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class AnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    stage_id = fields.Selection([
        ('draft', 'Draft'), 
        ('lc_review', 'LC review'), 
        ('pc_review', 'PC review'), 
        ('invoiceable', 'Invoiceable') 
        ], default='draft')

class AnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    @api.model
    def create(self, vals):
        if 'unit_amount' in vals:
            if vals['unit_amount'] % 0.25 != 0:
                vals['unit_amount'] = round(vals['unit_amount']*4)/4
        return super(AnalyticLine, self).create(vals)