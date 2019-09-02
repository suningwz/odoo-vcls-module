# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def add_new_program(self):
        action = self.env.ref('vcls-project.action_program').read()[0]
        action['view_mode'] = 'form'
        action['context'] = {'default_client_id': self.id,}
        return action