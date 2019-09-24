# -*- coding: utf-8 -*-

from odoo import _, api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def show_grid_cell(self, domain=[], column_value='', row_values={}):
        pass
