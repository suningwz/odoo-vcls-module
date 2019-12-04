# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class Project(models.Model):
    _inherit = 'project.project'

    contractual_budget = fields.Float(string="Contractual Budget")
    forecasted_budget = fields.Float(string="Forecasted Budget")
    realized_budget = fields.Float(string="Realized Budget")
    valued_budget = fields.Float(string="Valued Budget")
    invoiced_budget = fields.Float(string="Invoiced Budget")
    forecasted_hours = fields.Float(string="Forecasted Hours")
    realized_hours = fields.Float(string="Realized Hours")
    valued_hours = fields.Float(string="Valued Hours")
    invoiced_hours = fields.Float(string="Invoiced Hours")
    valuation_ratio = fields.Float(string="Valuation Ratio")


    @api.multi
    def _get_kpi(self):
        for project in self:
            project.contractual_budget = sum(project.task_ids.mapped('contractual_budget'))
            project.forecasted_budget = sum(project.task_ids.mapped('forecasted_budget'))
            project.realized_budget = sum(project.task_ids.mapped('realized_budget'))
            project.valued_budget = sum(project.task_ids.mapped('valued_budget'))
            project.invoiced_budget = sum(project.task_ids.mapped('invoiced_budget'))

            project.forecasted_hours = sum(project.task_ids.mapped('forecasted_hours'))
            project.realized_hours = sum(project.task_ids.mapped('realized_hours'))
            project.valued_hours = sum(project.task_ids.mapped('valued_hours'))
            project.invoiced_hours = sum(project.task_ids.mapped('invoiced_hours'))

            project.valuation_ratio = project.valued_hours / project.realized_hours if project.realized_hours else False
