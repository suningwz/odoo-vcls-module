# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    project_type_default = fields.Selection(
        selection_add = [('marketing', 'Marketing')],
        string='Project Type for Default',
    )

class Task(models.Model):
    
    _inherit = 'project.task'

    task_type = fields.Selection(
        selection_add = [('marketing','Marketing Campaign')],
        default='gen',
        string='Task Type',
        compute='_compute_task_type',
        store=True,)
    
    @api.depends('parent_id', 'project_id.project_type')
    def _compute_task_type(self):
        for task in self:
            if task.project_id.project_type == 'dev':
                if task.parent_id:
                    task.task_type = 'dev.task'
                else:
                    task.task_type = 'dev.vers'

            if task.project_id.project_type == 'marketing':
                task.task_type = 'marketing'
   
    organizer_id = fields.Many2one(
        'res.partner',
        string='Organizer'
    )
    business_line_id = fields.Many2one(
        'product.category',
        string='Business line',
        domain='[("is_business_line", "=", True)]'
    )
    country_group_id = fields.Many2one(
        'res.country.group',
        string='Country group',
    )

