# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
from datetime import datetime
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

    hourly_rate = fields.Float(
        readonly=True,
        default=False,
    )

    task_id = fields.Many2one('project.task', string="Task", group_expand='_read_forecast_tasks_vcls')
    start_date = fields.Date(compute='_get_start_end_date', store=True)
    end_date = fields.Date(compute='_get_start_end_date', store=True)
    deliverable_id = fields.Many2one(
        'product.deliverable',
        readonly=True, store=True,
        related='task_id.sale_line_id.product_id.deliverable_id'
    )

    @api.depends('task_id.date_start', 'task_id.date_end')
    def _get_start_end_date(self):
        for forecast in self:
            task_date_start = forecast.task_id.date_start
            task_date_end = forecast.task_id.date_end
            if task_date_start and task_date_end:
                forecast.start_date = task_date_start.date()
                forecast.end_date = task_date_end.date()
            else:
                forecast.start_date = self._default_start_date()
                forecast.end_date = self._default_end_date()

    # planned_hours on a task must be equal to the sum of forecast hours related to this task
    # only if this sum it is superior to zero.
    @api.multi
    def _force_forecast_hours(self):
        self = self.with_context(tracking_disable=True)
        for forecast in self:
            if not forecast.task_id:
                continue
            total_resource_hours = sum(self.search([('task_id', '=', forecast.task_id.id)]).mapped('resource_hours'))
            if total_resource_hours > 0:
                forecast.task_id.planned_hours = total_resource_hours

    @api.multi
    def write(self, values):
        for forecast in self:
            values['hourly_rate'] = forecast._get_hourly_rate(values)
            result = super(ProjectForecast, forecast).write(values)
        self.sudo()._force_forecast_hours()
        return result

    @api.model
    def create(self, values):
        h_r = self._get_hourly_rate(values)
        if h_r:
            values['hourly_rate'] = h_r
        forecast = super(ProjectForecast, self).create(values)
        forecast.sudo()._force_forecast_hours()
        return forecast

    @api.model
    def _read_forecast_tasks_vcls(self, tasks, domain, order):
        search_domain = [('id', 'in', tasks.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_id', 'child_of', [self.env.context['default_project_id']])] + search_domain
        return tasks.sudo().search(search_domain, order=order)
    
    @api.multi
    def _get_hourly_rate(self, vals):
        self.ensure_one()
        employee_id = vals.get('employee_id', self.employee_id.id)
        project_id = vals.get('project_id', self.project_id.id)
        if project_id and employee_id:
            rate_map = self.env['project.sale.line.employee.map'].search([
                ('employee_id', '=', employee_id),
                ('project_id', '=', project_id)],
                limit=1
            )
            if rate_map:
                return rate_map.price_unit
        return 0.0
