# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ContactExt(models.Model):

    _inherit = 'res.partner'
    
    ### CUSTOM FIELDS RELATED TO MARKETING PURPOSES ###

    no_mail = fields.Boolean(
        default = False,
        help = "Tick to exclude the contact from emailings.",
        string = 'Do Not Mail',
    )

    opted_in = fields.Boolean(
        default = False,
        string = 'OptedIn',
        help = 'Ticked if the client has specifically accepted to receive emailings.',
    )

    opted_out = fields.Boolean(
        default = False,
        string = 'OptedOut',
        help = 'Ticked if the client has specifically refused to receive emailings.',
    )

    

    external_ref_id = fields.Many2one(
        'res.partner',
        string = "External Reference",
        help = 'Document if the contact has been proposed by another contact.',
    )

    lead_source_id = fields.Many2one(
        'lead.source',
        string='Initial Lead Source',
    )

    initial_interest = fields.Char(
        string='Initial Interest',
    )