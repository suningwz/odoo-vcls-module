# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class Leads(models.Model):

    _inherit = 'crm.lead'

    marketing_project_id = fields.Many2one(
        comodel_name = 'project.project',
        string = "Lead Source",
        domain = [('project_type','=','marketing')]
    )

    marketing_task_id = fields.Many2one(
        comodel_name = 'project.task',
        string = "Related Campaign",
        domain = [('task_type','=','marketing')]
    )

