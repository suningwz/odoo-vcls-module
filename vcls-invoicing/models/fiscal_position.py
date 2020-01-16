# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    report_note = fields.Text('Report note')
