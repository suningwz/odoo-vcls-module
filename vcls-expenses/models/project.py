# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    expense_sheet_ids = fields.One2many(
        'hr.expense.sheet',
        'project_id',
    )

    allow_expense = fields.Boolean(default=True)

    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        We override the search of projects to improve type based filtering
        """
        search_type = self._context.get('search_type')

        #if we are in the context of a vcls custom search
        project_ids = super(Project, self)._search(args, offset, None, order, count=count, access_rights_uid=access_rights_uid)

        if search_type == 'project':
            projects = self.browse(project_ids)
            projects = projects.filtered(lambda p: p.project_type=='client')
            return projects.ids

        elif search_type == 'admin':
            projects = self.browse(project_ids)
            projects = projects.filtered(lambda p: p.project_type=='internal' and p.allow_expense)
            return projects.ids

        
        return project_ids