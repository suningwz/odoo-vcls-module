# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ContactExt(models.Model):

    _inherit = 'res.partner'
    
    ###  ###
    relation_ids = fields.Many2many(
        'res.partner.relation',
        readonly = True,
        string = 'Mapped Relations',
    )

    