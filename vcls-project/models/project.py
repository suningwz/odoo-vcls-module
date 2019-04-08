# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    project_type = fields.Selection([
        ('dev', 'Developement'),
        ('client', 'Client')],
        string = 'Project Type',
    )

    """
    version_ids = fields.One2many(
        'project.version',
        'project_id',
        string='All Versions',
        compute = '_get_versions',
        )

    version_id = fields.Many2one('project.version',
        string='Current Version',
        help='Currently Developed Version',
        )
    
    version_count = fields.Integer(
        string = 'Version Count',
        compute = '_get_versions',
    )

    ###################
    # COMPUTE METHODS #
    ###################

    @api.multi
    def _get_versions(self):
        for proj in self:
            proj.version_ids = self.env['project.version'].search([('project_id','=',proj.id)])
            proj.version_count = len(proj.version_ids)
    """
