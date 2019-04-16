# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ContactExt(models.Model):

    _inherit = 'res.partner'
    
    #################
    # CUSTOM FIELDS #
    #################

    evaluation_ids = fields.One2many(
        'survey.user_input',
        'supplier_id',
        string = 'Evaluations',
    )