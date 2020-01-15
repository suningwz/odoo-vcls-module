# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class Project(models.Model):

    _inherit = 'project.project'
    
    event_type = fields.Selection([
        ('conference', 'conference'),
        ('webinar', 'webinar'),
        ('other', 'other'),
    ], string='Event Type')

    project_type = fields.Selection(
        selection_add = [('marketing', 'Marketing')],
        string = 'Project Type',
    )


