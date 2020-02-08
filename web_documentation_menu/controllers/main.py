# -*- coding: utf-8 -*-
import logging

from odoo import http, models, fields, _
from odoo.addons.portal.controllers.web import Home

logger = logging.getLogger(__name__)


class Web(Home):

    @http.route('/get/user/documentation', type='json', auth="user")
    def get_user_documentation(self, **kw):
        documentation_url = http.request.env['ir.config_parameter'].sudo().get_param('web.documentation.url')
        return {
            'documentation_url': documentation_url,
        }
