# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_api_json_file_content = fields.Text(
        "google api json file content"
    )

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()

        if not self.user_has_groups('base.group_system'):
            return

        self.env['ir.config_parameter'].sudo().set_param(
            "Google_api_json_file_content",
            self.google_api_json_file_content
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        if self.user_has_groups('base.group_system'):
            params = self.env['ir.config_parameter'].sudo()
            res.update(
                google_api_json_file_content=params.get_param('google_api_json_file_content', default='')
            )
        return res

