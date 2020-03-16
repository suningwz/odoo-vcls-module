# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_name = fields.Char('Account name')
    swift = fields.Char('Swift')
    iban = fields.Char('Iban')
    bank_account_notes = fields.Text(string='Notes')

