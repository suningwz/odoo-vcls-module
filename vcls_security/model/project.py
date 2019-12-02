# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.osv import expression


class Task(models.Model):
    _inherit = 'project.task'

    # This will be used to avoid
    # an unknown bug (The bug: LC cannot edit his project's tasks)
    project_user_id = fields.Many2one(
        'res.users', related='project_id.user_id',
        store=True, readonly=True
    )


class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # Lead consultant cannot see project unless they are the project manager
        # This is only a visual constraint
        if self._context.get('only_show_mine_for_lc_group') and self.env.user.has_group('vcls_security.vcls_lc'):
            args = expression.AND([args, [('user_id', '=', self._uid)]])
        return super(Project, self)._search(args, offset, limit, order, count, access_rights_uid)
