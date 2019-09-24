# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    time_category_ids = fields.Many2many(
        'project.time_category',
        string='Time Categories',
        )
    connected_employee_seniority_level_id = fields.Many2one(
        comodel_name='hr.employee.seniority.level',
        compute='_get_connected_employee_seniority_level_id',
        string='Default Seniority'
    )

    @api.multi
    def _get_connected_employee_seniority_level_id(self):
        user_id = self.env.user.id
        connected_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
        seniority_level_id = connected_employee_id.seniority_level_id
        for line in self:
            line.connected_employee_seniority_level_id = seniority_level_id


class Project(models.Model):
    _inherit = 'project.project'

        
    @api.model #to be called from CRON job
    def update_project_manager(self):
        group = self.env.ref('project.group_project_manager')
        (self.env['res.users'].search([]) - self.search([]).mapped('user_id')).write({'groups_id': [(3, group.id)]})
        self.search([]).mapped('user_id').write({'groups_id': [(4, group.id)]})
    