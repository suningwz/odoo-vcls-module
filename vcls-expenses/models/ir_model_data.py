# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    def _remove_no_update(self, xml_id):
        ir_model_data_id = self.xmlid_lookup(xml_id)[0]
        query = 'UPDATE ir_model_data SET noupdate = FALSE WHERE id = %s'
        self._cr.execute(query, [ir_model_data_id])