# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class Leads(models.Model):

    _inherit = 'crm.lead'
    
    ### CUSTOM FIELDS RELATED TO MARKETING PURPOSES ###
    country_group_id = fields.Many2one(
        'res.country.group',
        string = "Geographic Area",
        compute = '_compute_country_group',
    )

    referent_id = fields.Many2one(
        'res.partner',
        string = 'Referred By',
    )

    functional_focus_id = fields.Many2one(
        'partner.functional.focus',
        string = 'Functional  Focus',
    )

    partner_seniority_id = fields.Many2one(
        'partner.seniority',
        string = 'Seniority',
    )

    client_activity_ids = fields.Many2many(
        'client.activity',
        string = 'Client Activity',
    )

    client_product_ids = fields.Many2many(
        'client.product',
        string = 'Client Product',
    )

    industry_id = fields.Many2one(
        'res.partner.industry',
        string = "Industry",
    )

    #date fields

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('country_id')
    def _compute_country_group(self):
        for contact in self:
            #groups = contact.country_id.country_group_ids.filtered([('group_type','=','BD')])
            groups = contact.country_id.country_group_ids
            if groups:
                contact.country_group_id = groups[0]