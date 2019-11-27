# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, http

from odoo.exceptions import UserError, ValidationError

class MailActivity(models.Model):
    
    _inherit = 'mail.activity'

    def go_to_record(self):
        self.ensure_one()
        url = http.request.env['ir.config_parameter'].get_param('web.base.url')
        link = "{}/web#id={}&model={}".format(url, self.res_id, self.res_model)
        return {
            'type': 'ir.actions.act_url',
            'url': link,
            'target': 'current',
        }
