# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class Leads(models.Model):

    _inherit = 'crm.lead'

    marketing_project_id = fields.Many2one(
        comodel_name = 'project.marketing',
        string = "Campaign Type",
    )

    marketing_task_id = fields.Many2one(
        comodel_name = 'task.marketing',
        string = "Campaign",
    )

