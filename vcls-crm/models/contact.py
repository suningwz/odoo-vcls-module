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

    ### MARKETING FIELDS FOR TRACEABILITY ###
    
    #Marketing fields
    opted_in = fields.Boolean(
        string = 'Opted In',
    )

    opted_out = fields.Boolean(
        string = 'Opted Out',
    )

    vcls_contact_id = fields.Many2one(
        'res.users',
        string = "Initial Contact",
        domain = "[('employee','=',True)]",
    )