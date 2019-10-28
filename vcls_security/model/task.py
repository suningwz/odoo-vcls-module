# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError


class Task(models.Model):
    _inherit = 'project.task'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        if operation in ('create', 'unlink') and \
                self.env.user.has_group('vcls_security.group_vcls_consultant'):
            # vcls_consultantuser has only read and write access to task
            if raise_exception:
                raise AccessError(_("Sorry, you are not allowed to modify this document."))
            else:
                return False
        return super(Task, self).check_access_rights(operation, raise_exception)


    @api.multi
    def check_access_rule(self, operation):
        if operation == 'write' and self.env.user.has_group('vcls_security.group_vcls_consultant'):
            user = self.env.user
            for task in self:
                # vcls_consultantuser has write access only on his own tasks
                if task.user_id != user:
                    raise AccessError(_("Sorry, you are not allowed to modify this document."))
        return super(Task, self).check_access_rule(operation)
