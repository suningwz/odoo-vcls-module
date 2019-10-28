# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Invoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        has_access = self.env['ir.model.access']._disable_cwd_access(
            self._name, operation,
            'vcls_security.vcls_account_manager',
            'vcls_security.group_bd_admin',
            raise_exception)
        if not has_access:
            return has_access
        return super(Invoice, self).check_access_rights(operation, raise_exception)


class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        has_access = self.env['ir.model.access']._disable_cwd_access(
            self._name, operation,
            'vcls_security.vcls_account_manager',
            'vcls_security.group_bd_admin',
            raise_exception)
        if not has_access:
            return has_access
        return super(InvoiceLine, self).check_access_rights(operation, raise_exception)
