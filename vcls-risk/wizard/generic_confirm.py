# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class GenericConfirm(models.TransientModel):
    _name = 'generic.confirm.wizard'
    _description = 'Generic Confirm Wizard'

    name = fields.Char()

    @api.multi
    def confirm(self):
        return True

    @api.multi
    def cancel(self):
        return False
        
