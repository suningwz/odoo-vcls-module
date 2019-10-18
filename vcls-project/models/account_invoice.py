# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    project_ids = fields.Many2many(
        string='Projects',
        comodel_name="project.project",
        relation="project_out_invoice_rel",
        column1="invoice_id",
        column2="project_id",
        copy=False, readonly=True
    )
