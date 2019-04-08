# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    business_value = fields.Selection([
        ('1', 'Minor'),
        ('2', 'Moderate'),
        ('3', 'Strong'),
        ('4', 'Major')],
        string = 'Business Value',
    )

    dev_effort = fields.Selection([
        ('1', 'Small'),
        ('2', 'Medium'),
        ('3', 'Large'),
        ('4', 'Xtra Large')],
        string = 'Effort Assumption',
    )

    task_type = fields.Selection([
        ('gen','Generic'),
        ('dev.vers','Development Version'),
        ('dev.task','Development Task'),],
        default = 'gen',
        string = 'Task Type',
        compute = '_compute_task_type',)

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('parent_id','project_id.project_type')
    def _compute_task_type(self):
        for task in self:
            if task.project_id.project_type == 'dev':
                if task.parent_id:
                    task.task_type = 'dev.task'
                else:
                    task.task_type = 'dev.vers'
