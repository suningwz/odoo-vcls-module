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
    user_id = fields.Many2one(
        'res.users', 
        string='Account Manager', 
        track_visibility='onchange', 
        #default='_default_am',
        )

    """name = fields.Char(
        required = True,
        compute = '_compute_name',
        inverse = '_get_name',
    )"""

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

    product_category_id = fields.Many2one(
        'product.category',
        string = 'Business Line',
        domain = "[('parent_id','=',False)]"
    )

    #date fields
    expected_start_date = fields.Date(
        string="Expected Project Start Date",
    )

    won_reason = fields.Many2one('crm.won.reason', string='Won Reason', index=True, track_visibility='onchange')

    internal_ref = fields.Char(
        string="Ref",
        readonly = True,
        store = True,
        compute = '_compute_internal_ref',
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
    
    @api.depends('partner_id')
    def _compute_internal_ref(self):
        if self.partner_id:
            if not self.partner_id.altname:
                raise UserError("Please document ALTNAME for the client {}".format(self.partner_id.name))

            next_index = self.partner_id.core_process_index+1 or 1
            self.partner_id.core_process_index = next_index
            self.internal_ref = "{}-{:03}".format(self.partner_id.altname,next_index)

    """
    @api.depends('internal_ref')
    def _compute_name(self):
        for lead in self:
            lead.name = lead.build_name()

    @api.onchange('name')
    def _get_name(self):
        self.name = self.build_name()

    def build_name(self):
        for lead in self:
            if not lead.name:
                temp = ""
            else:
                temp = lead.name

            if lead.internal_ref and temp.find(lead.internal_ref)==-1: #if the ref is not yet in the name
                return "{} | {}".format(lead.internal_ref,lead.name)
    """
    
    """@api.onchange('partner_id','country_id')
    def _change_am(self):
        for lead in self:
            lead.user_id = lead.guess_am()"""

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
        data = super()._create_lead_partner_data(name,is_company,parent_id)
        data['country_group_id'] = self.country_group_id
        data['referent_id'] = self.referent_id
        data['functional_focus_id'] = self.functional_focus_id
        data['partner_seniority_id'] = self.partner_seniority_id
        data['industry_id'] = self.industry_id
        data['client_activity_ids'] = self.client_activity_ids
        data['client_product_ids'] = self.client_product_ids

        return data

    @api.multi
    def _convert_opportunity_data(self, customer, team_id=False):
        """ Extract the data from a lead to create the opportunity
            :param customer : res.partner record
            :param team_id : identifier of the Sales Team to determine the stage
        """
        data = super()._convert_opportunity_data(customer, team_id)
        data['country_group_id'] = self.country_group_id
        data['referent_id'] = self.referent_id
        data['functional_focus_id'] = self.functional_focus_id
        data['partner_seniority_id'] = self.partner_seniority_id
        data['industry_id'] = self.industry_id
        data['client_activity_ids'] = self.client_activity_ids
        data['client_product_ids'] = self.client_product_ids
        data['product_category_id'] = self.product_category_id
        
        return data

    
    """
    @api.multi
    def _set_op_ref(self,partner_id=False):
        partner = partner_id or self.partner_id

        if not partner.altname:
            raise UserError("Please document ALTNAME for the client {}".format(partner.name))

        next_index = partner.core_process_index+1 or 1
        partner.core_process_index = next_index
        return "{}-{:03}".format(partner.altname,next_index)
    """

    
    ###############
    # ORM METHODS #
    ###############

    """
    @api.model
    def name_create(self, name):

        context = dict(self._context or {})
        raise UserError("{}".format(context))

        res = super(Lead, self).name_create(name)
        return res
    """
    """
    @api.model
    def create(self, vals):
        context = dict(self._context or {})

        #If we have a partner
        partner_id = vals.get('partner_id') or context.get('default_partner_id')
        if partner_id and vals.get('type') == 'opportunity':
            vals['internal_ref'] = self._set_op_ref(self.env['res.partner'].browse(partner_id))

        # context: no_log, because subtype already handle this
        return super(Leads, self.with_context(context, mail_create_nolog=True)).create(vals)
    """
    