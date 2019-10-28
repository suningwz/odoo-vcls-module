# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    def _disable_cwd_access(self, model, mode='read', group=None, allowed_group=None, raise_exception=True):
        """
        Disable create/write/unlink access for a specific model and group
        :param model: name of the model
        :param mode: the operation read/create/read/unlink
        :param group: the name of group
        :param raise_exception: raise exception or not
        :return: Boolean
        """
        if not group or (allowed_group and self.env.user.has_group(allowed_group)):
            return True
        if mode in ('write', 'create', 'unlink') and \
                self.env.user.has_group(group):
            if raise_exception:
                raise AccessError(_("Sorry, you are not allowed to modify this document."))
            else:
                return False
        return True
