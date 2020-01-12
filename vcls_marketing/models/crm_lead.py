# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class Leads(models.Model):

    _inherit = 'crm.lead'

    marketing_project_id = fields.Many2one(
        comodel_name = 'project.marketing',
        string = "Lead Source",
    )

    marketing_task_id = fields.Many2one(
        comodel_name = 'task.marketing',
        string = "Related Campaign",
    )

