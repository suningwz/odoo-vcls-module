# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class Leads(models.Model):

    _inherit = 'crm.lead'

    ###################
    # DEFAULT METHODS #
    ###################

    def _default_am(self):
        return self.guess_am()
    
    ### CUSTOM FIELDS RELATED TO MARKETING PURPOSES ###
    user_id = fields.Many2one('res.users', string='Account Manager', track_visibility='onchange', default='_default_am')

    country_group_id = fields.Many2one(
        'res.country.group',
        string = "Geographic Area",
        compute = '_compute_country_group',
    )

    referent_id = fields.Many2one(
        'res.partner',
        string = 'Referent',
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
    expected_start_date = fields.Date(
        string="Expected Project Start Date",
    )

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('country_id')
    def _compute_country_group(self):
        for lead in self:
            groups = lead.country_id.country_group_ids
            if groups:
                lead.country_group_id = groups[0]
    
    @api.onchange('partner_id','country_id')
    def _change_am(self):
        for lead in self:
            lead.user_id = lead.guess_am()

    ################
    # TOOL METHODS #
    ################

    def guess_am(self):
        if self.partner_id.user_id:
            return self.partner_id.user_id
        elif self.country_group_id.default_am:
            return self.country_group_id.default_am
        #elif self.team_id.
        else:
            return False

    @api.multi
    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        """ extract data from lead to create a partner
            :param name : furtur name of the partner
            :param is_company : True if the partner is a company
            :param parent_id : id of the parent partner (False if no parent)
            :returns res.partner record
        """
        email_split = tools.email_split(self.email_from)
        return {
            'name': name,
            'user_id': self.env.context.get('default_user_id') or self.user_id.id,
            'comment': self.description,
            'team_id': self.team_id.id,
            'parent_id': parent_id,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': email_split[0] if email_split else False,
            'title': self.title.id,
            'function': self.function,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'website': self.website,
            'is_company': is_company,
            'type': 'contact',
            'country_group_id': self.country_group_id,
            'referent_id': self.referent_id,
            'functional_focus_id': self.functional_focus_id,
            'partner_seniority_id': self.partner_seniority_id,
            'industry_id': self.industry_id,
            'client_activity_ids': self.client_activity_ids,
            'client_product_ids': self.client_product_ids
        }

    @api.multi
    def _convert_opportunity_data(self, customer, team_id=False):
        """ Extract the data from a lead to create the opportunity
            :param customer : res.partner record
            :param team_id : identifier of the Sales Team to determine the stage
        """
        if not team_id:
            team_id = self.team_id.id if self.team_id else False
        value = {
            'planned_revenue': self.planned_revenue,
            'probability': self.probability,
            'name': self.name,
            'partner_id': customer.id if customer else False,
            'type': 'opportunity',
            'date_open': fields.Datetime.now(),
            'email_from': customer and customer.email or self.email_from,
            'phone': customer and customer.phone or self.phone,
            'date_conversion': fields.Datetime.now(),
            'country_group_id': self.country_group_id,
            'referent_id': self.referent_id,
            'functional_focus_id': self.functional_focus_id,
            'partner_seniority_id': self.partner_seniority_id,
            'industry_id': self.industry_id,
            'client_activity_ids': self.client_activity_ids,
            'client_product_ids': self.client_product_ids
        }
        if not self.stage_id:
            stage = self._stage_find(team_id=team_id)
            value['stage_id'] = stage.id
            if stage:
                value['probability'] = stage.probability
        return value