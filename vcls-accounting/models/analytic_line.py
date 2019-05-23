# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
"""
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id(self):
        # WE temporary deactivate this constrain to ensure leave to be approved by other countries
        pass
        
        for line in self:
            if line.account_id.company_id and line.company_id.id != line.account_id.company_id.id:
                raise ValidationError(_('The selected account belongs to another company that the one you\'re trying to create an analytic item for'))
        """