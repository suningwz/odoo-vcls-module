# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.exceptions import AccessError


class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # Lead consultant cannot see project unless they are the project manager
        # This is only a visual constraint
        if self._context.get('only_show_mine_for_lc_group') and self.env.user.has_group('vcls_security.vcls_lc'):
            args = expression.AND([args, [('user_id', '=', self._uid)]])
        return super(Project, self)._search(args, offset, limit, order, count, access_rights_uid)

    # @api.multi
    # def check_access_rule(self, operation):
    #     if not self.env.user.has_group('vcls_security.group_bd_admin'):
    #         if operation == 'write':
    #             if not self.env.user.has_group('project.group_project_manager') and\
    #                     self.env.user.has_group('vcls_security.vcls_account_manager'):
    #                 user = self.env.user
    #                 for project in self:
    #                     # vcls_account_manager user has write access only on
    #                     # projects where he is account manager of the related partner
    #                     if project.partner_id.user_id != user:
    #                         raise AccessError(_("Sorry, you are not allowed to modify this document."))
    #     return super(Project, self).check_access_rule(operation)
