# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Invoice(models.Model):
    _inherit = 'account.invoice'


class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
