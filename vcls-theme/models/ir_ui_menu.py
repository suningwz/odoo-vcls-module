# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    # delete the lc root menu if connected user
    # is not manager of at least one project
    def get_user_roots(self):
        menu_ids = super(IrUiMenu, self).get_user_roots()
        if not self.env['project.project'].sudo().search([('user_id', '=', self._uid)], limit=1):
            menu_ids -= self.env.ref('vcls-theme.menu_lc_root')
        return menu_ids

    @api.model
    @tools.ormcache_context('self._uid', 'debug', 'bool(frozenset(self.env.user.project_ids.ids))', keys=('lang',))
    def load_menus(self, debug):
        # We clear the cache of this method
        # as a new parameter is added to the ormcache_context decorator
        self.load_menus.clear_cache(self)
        return super(IrUiMenu, self).load_menus(debug)
