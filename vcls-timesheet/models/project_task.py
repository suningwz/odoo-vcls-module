# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    time_category_ids = fields.Many2many(
        'project.time_category',
        string='Time Categories',
        )

class Project(models.Model):
    _inherit = 'project.project'

        
    @api.model #to be called from CRON job
    def update_project_manager(self):
        group = self.env.ref('project.group_project_manager')
        (self.env['res.users'].search([]) - self.search([]).mapped('user_id')).write({'groups_id': [(3, group.id)]})
        self.search([]).mapped('user_id').write({'groups_id': [(4, group.id)]})
    