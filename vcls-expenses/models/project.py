# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    expense_sheet_ids = fields.One2many(
        'hr.expense.sheet',
        'project_id',
    )
