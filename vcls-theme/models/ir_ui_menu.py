# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def get_user_roots(self):
        menu_ids = super(IrUiMenu, self).get_user_roots()
        if not self.env['project.project'].sudo().search([('user_id', '=', self._uid)], limit=1):
            menu_ids -= self.env.ref('vcls-theme.menu_lc_root')
        return menu_ids
