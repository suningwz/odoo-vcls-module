# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    project_type = fields.Selection([
        ('dev', 'Developement'),
        ('client', 'Client')],
        string = 'Project Type',
    )
