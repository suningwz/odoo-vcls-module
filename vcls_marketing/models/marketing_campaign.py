# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class MarketingCampaign(models.Model):

    _inherit = 'marketing.campaign'

    marketing_project_id = fields.Many2one(
        comodel_name = 'project.project',
        string = "Related Markeing Project",
        domain = [('project_type','=','marketing')],
    )

    marketing_task_id = fields.Many2one(
        comodel_name = 'project.task',
        string = "Related Task",
        domain = [('task_type','=','marketing')]
    )

   

