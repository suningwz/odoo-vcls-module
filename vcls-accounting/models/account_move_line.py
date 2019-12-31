# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AccountAnalyticLine(models.Model):
    _inherit = 'account.move.line'
    
    external_account = fields.Char(
        related = 'partner_id.external_account'
    )

    journal_code = fields.Char(
        related = 'journal_id.code'
    )

    account_code = fields.Char(
        related = 'account_id.code'
    )