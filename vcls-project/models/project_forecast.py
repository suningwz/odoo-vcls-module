# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class ProjectForecast(models.Model):
    _inherit = 'project.forecast'

    department_id = fields.Many2one(
        'hr.department',
        related='employee_id.department_id',
        string='Department',
        store=True,
        readonly=True
    )

    # planned_hours on a task must be equal to the sum of forecast hours related to this task
    # only if this sum it is superior to zero.
    @api.multi
    def _force_forecast_hours(self):
        for forecast in self:
            if forecast.resource_hours <= 0 or not forecast.task_id:
                return
            total_resource_hours = sum(self.search([('task_id', '=', forecast.task_id.id)]).mapped('resource_hours'))
            if total_resource_hours > 0:
                forecast.task_id.planned_hours = total_resource_hours

    @api.multi
    def write(self, values):
        result = super(ProjectForecast, self).write(values)
        if values.get('resource_hours', 0) > 0:
            self.sudo()._force_forecast_hours()
        return result

    @api.model
    def create(self, values):
        forecast = super(ProjectForecast, self).create(values)
        forecast.sudo()._force_forecast_hours()
        return forecast
