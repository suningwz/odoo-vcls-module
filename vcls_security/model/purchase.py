# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def check_access_rule(self, operation):
        if operation == 'write' and self.env.user.has_group('vcls_security.vcls_account_manager'):
            for state in self.mapped('state'):
                # vcls_account_manager does not have the right to edit purchase when they confirmed
                if state not in ('draft', 'sent', 'to approve'):
                    raise AccessError(_("Sorry, you are not allowed to modify this document in this state."))
        return super(PurchaseOrder, self).check_access_rule(operation)
