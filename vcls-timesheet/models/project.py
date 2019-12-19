# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class Project(models.Model):
    _inherit = 'project.project'

    contractual_budget = fields.Float(string="Contractual Budget",readonly=True)
    forecasted_budget = fields.Float(string="Forecasted Budget",readonly=True)
    realized_budget = fields.Float(string="Realized Budget",readonly=True)
    valued_budget = fields.Float(string="Valued Budget",readonly=True)
    invoiced_budget = fields.Float(string="Invoiced Budget",readonly=True)
    forecasted_hours = fields.Float(string="Forecasted Hours",readonly=True)
    realized_hours = fields.Float(string="Realized Hours",readonly=True)
    valued_hours = fields.Float(string="Valued Hours",readonly=True)
    invoiced_hours = fields.Float(string="Invoiced Hours",readonly=True)
    valuation_ratio = fields.Float(string="Valuation Ratio",readonly=True)

    pc_budget = fields.Float(string="PC Review Budget",readonly=True)
    cf_budget = fields.Float(string="Carry Forward Budget",readonly=True)
    pc_hours = fields.Float(string="PC Review Hours",readonly=True)
    cf_hours = fields.Float(string="Carry Forward Hours",readonly=True)


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

            project.pc_budget = sum(project.task_ids.mapped('pc_budget'))
            project.cf_budget = sum(project.task_ids.mapped('cf_budget'))
            project.pc_hours = sum(project.task_ids.mapped('pc_hours'))
            project.cf_hours = sum(project.task_ids.mapped('cf_hours'))

            project.valuation_ratio = 100.0*(project.valued_hours / project.realized_hours) if project.realized_hours else False
