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

    hourly_rate = fields.Float(
        readonly=True,
        default=False,
    )

    task_id = fields.Many2one('project.task', string="Task", group_expand='_read_forecast_tasks_vcls')

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
                #forecast.task_id.with_context(tracking_disable=True).write({'planned_hours':total_resource_hours})
                #_logger.info("new hours {}".format(total_resource_hours))
            
            #We get the price of the related rate (if exists)
            rate_map = self.env['project.sale.line.employee.map'].search([('employee_id','=',forecast.employee_id),('project_id','=',forecast.project_id)])
            if rate_map:
                forecast.hourly_rate = rate_map[0].price_unit

    @api.multi
    def write(self, values):
        result = super(ProjectForecast, self).write(values)
        self.sudo()._force_forecast_hours()
        return result

    @api.model
    def create(self, values):
        forecast = super(ProjectForecast, self).create(values)
        forecast.sudo()._force_forecast_hours()
        return forecast

    @api.model
    def _read_forecast_tasks_vcls(self, tasks, domain, order):
        search_domain = [('id', 'in', tasks.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_id', 'child_of', [self.env.context['default_project_id']])] + search_domain
        return tasks.sudo().search(search_domain, order=order)
