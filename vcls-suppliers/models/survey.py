# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class Evaluation(models.Model):

    _inherit = 'survey.user_input'
    
    #################
    # CUSTOM FIELDS #
    #################

    supplier_id = fields.Many2one(
        'res.partner',
    )