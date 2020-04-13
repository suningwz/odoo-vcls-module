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

    base_currency_id = fields.Many2one('res.currency',compute="_compute_base_values", store=True)
    debit_base_currency = fields.Monetary(default=0.0, currency_field='base_currency_id',compute="_compute_base_values",store=True)
    credit_base_currency = fields.Monetary(default=0.0, currency_field='base_currency_id',compute="_compute_base_values",store=True)
    convertion_rate = fields.Float(compute="_compute_base_values",store=True)

    @api.depends('debit','credit','company_currency_id')
    def _compute_base_values(self):
        for line in self.filtered(lambda l: l.debit>0 and l.company_currency_id):
            currency_id = self.env.ref('base.EUR')
            debit_conv = line.company_currency_id._convert(
                line.debit,
                currency_id,
                self.env.user.company_id,
                line.date or fields.Datetime.now(),
            )
            line.write({
                'base_currency_id':currency_id.id,
                'convertion_rate':line.company_currency_id.rate,
                'debit_base_currency':debit_conv,
            })

        for line in self.filtered(lambda l: l.credit>0 and l.company_currency_id):
            currency_id = self.env.ref('base.EUR')
            credit_conv = line.company_currency_id._convert(
                line.credit,
                currency_id,
                self.env.user.company_id,
                line.date or fields.Datetime.now(),
            )
            line.write({
                'base_currency_id':currency_id.id,
                'convertion_rate':line.company_currency_id.rate,
                'credit_base_currency':credit_conv,
            })