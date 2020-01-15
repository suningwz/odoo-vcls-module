# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class ProjectMarketing(models.Model):
    _name = 'project.marketing'
    _inherit = 'project.project'
    _description = 'Project marketing'

    event_type = fields.Selection([
        ('conference', 'conference'),
        ('webinar', 'webinar'),
        ('other', 'other'),
    ], string='Event Type')


    project_type = fields.Selection(
        selection_add = [('marketing', 'Marketing')],
        string = 'Project Type',
        default = 'marketing',
        readonly = True,
    )

    company_id = fields.Many2one(default=lambda self: self.env.ref('base.main_company'))


