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

    ###############
    # ORM METHODS #
    ###############
    @api.model
    def create(self, vals):

        project = super(Project, self).create(vals)

        if project.project_type == 'marketing':
            project.company_id = self.env.ref('base.main_company')
            wt = self.env['resource.calendar'].search([('company_id','=',project.company_id.id),('effective_hours','=',40.0)],limit=1)
            if wt:
                project.resource_calendar_id = wt
            else:
                project.resource_calendar_id = False


