# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError


class Task(models.Model):
    _inherit = 'project.task'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        if operation in ('create', 'unlink') and \
                (self.env.user.has_group('vcls_security.group_vcls_consultant') or
                 self.env.user.has_group('vcls_security.vcls_account_manager')):
            # vcls_consultant and vcls_account_manager users have only read and write access to tasks
            if raise_exception:
                raise AccessError(_("Sorry, you are not allowed to modify this document."))
            else:
                return False
        return super(Task, self).check_access_rights(operation, raise_exception)

    @api.multi
    def check_access_rule(self, operation):
        if operation == 'write':
            user = self.env.user
            if self.env.user.has_group('vcls_security.group_vcls_consultant'):
                for task in self:
                    # vcls_consultant user has write access only on his own tasks
                    if task.user_id != user:
                        raise AccessError(_("Sorry, you are not allowed to modify this document."))
            if self.env.user.has_group('vcls_security.vcls_account_manager'):
                for task in self:
                    # vcls_account_manager user has write access only on
                    # tasks where he is account manager of the related partner
                    if task.project_id.partner_id.user_id != user:
                        raise AccessError(_("Sorry, you are not allowed to modify this document."))
        return super(Task, self).check_access_rule(operation)
