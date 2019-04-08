# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    project_type = fields.Selection([
        ('dev', 'Developement'),
        ('client', 'Client')],
        string = 'Project Type',
    )

    version_ids = fields.One2many(
        'project.version',
        'project_id',
        string='All Versions',
        )

    version_id = fields.Many2one('project.version',
        string='Current Version',
        help='Currently Developed Version',
        )
