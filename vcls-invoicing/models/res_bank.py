# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_name = fields.Char('Account name')
    swift = fields.Char('Swift')
    iban = fields.Char('Iban')
    bank_account_notes = fields.Text(string='Notes', translate=True)

    @api.multi
    def name_get(self, context=None):
        result = []
        for account in self:
            tmp_name = "{} | {}".format(account.account_name, account.acc_number)
            result.append((account.id, tmp_name))
            return result
