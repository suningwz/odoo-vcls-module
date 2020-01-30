# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class MarketingCampaign(models.Model):

    _inherit = 'marketing.campaign'

    marketing_project_id = fields.Many2one(
        comodel_name = 'project.project',
        string = "Related Marketing Project",
        domain = [('project_type','=','marketing')],
    )

    marketing_task_id = fields.Many2one(
        comodel_name = 'project.task',
        string = "Related Task",
        domain = [('task_type','=','marketing')]
    )

class MailingCampaign(models.Model):

    _inherit = 'mail.mass_mailing.campaign'

    marketing_project_id = fields.Many2one(
        comodel_name = 'project.project',
        string = "Related Marketing Project",
        domain = [('project_type','=','marketing')],
    )

    marketing_task_id = fields.Many2one(
        comodel_name = 'project.task',
        string = "Related Task",
        domain = [('task_type','=','marketing')]
    )

   

