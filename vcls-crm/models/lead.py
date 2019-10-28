# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import date
import datetime

import logging
_logger = logging.getLogger(__name__)


class ResoucesLeads(models.Model):

    _name = 'crm.resource.lead'
    _description = 'resource for lead'
    
    project_role_id = fields.Many2one(
        'hr.project_role', string='Seniority')
    number = fields.Float('Number')

class LeadStage(models.Model):
    _name = 'crm.lead.stage'
    _description = 'stage for lead'

    name = fields.Char(
        required = True,
        string = 'Name'
    )
    
    active = fields.Boolean(default = True)


class Leads(models.Model):

    _inherit = 'crm.lead'
    altname = fields.Char('Altname')
    hide_altname = fields.Boolean()

    @api.onchange('partner_id', 'partner_name')
    def onchange_info(self):
        hide_altname = False
        if self.partner_id or not self.partner_name:
            hide_altname = True
        self.hide_altname = hide_altname

    ###################
    # DEFAULT METHODS #
    ###################


    def _default_am(self):
        return self.guess_am()

    @api.model
    def _default_lead_stage(self):
        try:
            return self.env.ref('vcls-crm.lead_open')
        except:
            return self.env['crm.lead.stage']


    ####################
    # OVERRIDEN FIELDS #
    ####################

    company_id = fields.Many2one(string = 'Trading Entity', default = lambda self: self.env.ref('vcls-hr.company_VCFR'))

    source_id = fields.Many2one('utm.source', "Initial Lead Source")

    user_id = fields.Many2one(
        'res.users', 
        string='Account Manager', 
        track_visibility='onchange', 
        domain=lambda self: [("groups_id", "=", self.env['res.groups'].search([('name','=', 'Account Manager')]).id)]
        )

    #################
    # CUSTOM FIELDS #
    #################

    # Related fields in order to avoid mismatch & errors
    opted_in = fields.Boolean(
        related = 'partner_id.opted_in',
        string = 'Opted In'
    )

    opted_out = fields.Boolean(
        related = 'partner_id.opted_out',
        string = 'Opted Out'
    )

    opted_in_date = fields.Datetime(
        string = 'Opted In Date',
        default = lambda self: self._get_default_opted_in_date(),
    )
 
    lead_stage_id = fields.Many2one(
        'crm.lead.stage',
        string = 'Lead Stage',
        default = _default_lead_stage,
        )

    ### CUSTOM FIELDS RELATED TO MARKETING PURPOSES ###
    
    
    company_id = fields.Many2one(default = '')

    country_group_id = fields.Many2one(
        'res.country.group',
        string = "Geographic Area",
        compute = '_compute_country_group',
    )

    referent_id = fields.Many2one(
        'res.partner',
        string = 'Referee',
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

    scope_of_work = fields.Html(
        placeholder = 'Summary in bullet points'
    )

    product_category_id = fields.Many2one(
        'product.category',
        string = 'Business Line',
        domain = "[('is_business_line','=',True)]"
    )

    
    #date fields
    expected_start_date = fields.Date(
        string="Expected Project Start Date",
    )


    won_reason = fields.Many2one(
        'crm.won.reason'
    )

    won_reasons = fields.Many2many(
        'crm.won.reason',
        string='Won Reasons',
        index=True,
        track_visibility='onchange'
    )

    lost_reasons = fields.Many2many(
        'crm.lost.reason',
        string='Lost Reasons',
        index=True,
        track_visibility='onchange'
    )

    internal_ref = fields.Char(
        string="Ref",
        store = True,
        #compute = '_compute_internal_ref',
        #inverse = '_set_internal_ref',
    )
    
    technical_adv_id = fields.Many2one(
        'hr.employee', 
        string='PIC', 
        track_visibility='onchange', 
        )
    
    support_team = fields.Many2many(
        'hr.employee', 
        string='Other Technical Experts', 
        )
    
    resources_ids = fields.Many2many(
        'crm.resource.lead', 
        string='Resources', 
        )
    
    CDA = fields.Boolean('CDA signed')
    MSA = fields.Boolean('MSA valid')
    sp_folder = fields.Char('Sharepoint Folder')
    
    contract_type = fields.Selection([('saleorder', 'Sale Order'),
                                      ('workorder', 'Work Order'),
                                      ('termandcondition', 'Terms and conditions'),])


    #is_support_user = fields.Boolean(compute='_compute_is_support_user', store=False)

    app_country_group_id = fields.Many2one(
        'res.country.group',
        string = "Application Geographic Area",
    )

    therapeutic_area_ids = fields.Many2many(
        'therapeutic.area',
        string ='Therapeutic Area',
    )
    
    targeted_indication_ids = fields.Many2many(
        'targeted.indication',
        string ='Targeted Indication',
    )
    
    stage_development_id = fields.Many2one(
        'stage.development',
        string ='Stage of Development',
    )

    meet_story = fields.Char(
    )

    initial_vcls_contact = fields.Many2one(
        'res.users', 
        default=lambda self: self.env.user.id,
        string='VCLS Initial Contact'
    )

    age = fields.Char(
        compute = '_compute_lead_age'
    )

    conversion_date = fields.Date(string = 'Lead to Opp date')

    #name = fields.Char() We don't compute, it breaks too much usecases

    lead_history = fields.Many2many(comodel_name="crm.lead", relation="crm_lead_rel", column1="crm_lead_id1")

    ### MIDDLE NAME ###

    contact_middlename = fields.Char("Middle name")

    ### WON / LOST DESCRIPTION ###
    won_lost_description = fields.Char(string = 'Won/Lost details')

    linkedIn_url = fields.Char(string = 'LinkedIn profile')

    unsubscribed_campaign_id = fields.Many2one('utm.campaign', string = 'Opted Out Campaign')

    opted_out_date = fields.Datetime(
        string = 'Opted Out Date', 
        related = 'unsubscribed_campaign_id.create_date'
    )

    gdpr_status = fields.Selection(
        [
            ('undefined', 'Undefined'),
            ('in', 'In'),
            ('out', 'Out'),
        ],
        string = 'GDPR Status',
        compute = '_compute_gdpr'
    )

    @api.model
    def create(self, vals):
        #############
        if vals.get('contact_name', False) and vals.get('contact_lastname', False) and vals.get('contact_middlename', False):
                vals['name'] = vals['contact_name'] + " " + vals['contact_middlename'] + " " + vals['contact_lastname']
        elif vals.get('contact_name', False) and vals.get('contact_lastname', False):
                vals['name'] = vals['contact_name'] + " " + vals['contact_lastname']
        #############
        lead = super(Leads, self).create(vals)
        # VCLS MODS
        if lead.type == 'lead':
            lead.message_ids[0].subtype_id = self.env.ref('vcls-crm.lead_creation')
        elif lead.type == 'opportunity' and lead.partner_id:
            lead.write({'type':'opportunity'})
           
        # END OF MODS
        return lead
    
    def write(self, vals):
        if (vals.get('type',False) == 'lead' or self.type == 'lead'):
            if vals.get('contact_name', False) and vals.get('contact_lastname', False) and vals.get('contact_middlename', False):
                    vals['name'] = vals['contact_name'] + " " + vals['contact_middlename'] + " " + vals['contact_lastname']
            elif vals.get('contact_name', False) and vals.get('contact_lastname', False):
                    vals['name'] = vals['contact_name'] + " " + vals['contact_lastname']

        #we manage the reference of the opportunity, if we change the type or update an opportunity not having a ref defined
        #_logger.info("INTERNAL REF {}".format(vals.get('internal_ref',self.internal_ref)))
        if (vals.get('type',False) == 'opportunity' or self.type == 'opportunity') and not vals.get('internal_ref',self.internal_ref):
            client = self.env['res.partner'].browse(vals.get('partner_id',self.partner_id.id)) #if a new client defined or was already existing
            if client:
                vals['internal_ref']=client._get_new_ref()[0]
            else:
                vals['internal_ref']=False
        
        vals['name']=self.build_opp_name(vals.get('internal_ref',self.internal_ref),vals.get('name',self.name))

        _logger.info("{}".format(vals))
        return super(Leads, self).write(vals)

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('country_id')
    def _compute_country_group(self):
        for lead in self:
            groups = lead.country_id.country_group_ids
            if groups:
                lead.country_group_id = groups[0]
    
    @api.depends('create_date', 'type', 'conversion_date')
    def _compute_lead_age(self):
        for lead in self:
            if lead.conversion_date != False:
                reference = lead.conversion_date.date()
            elif lead.create_date != False:
                reference = lead.create_date.date()
            else:
                reference = date.today()
            today = date.today()
            delta = today - reference
            if delta.days == 1:
                lead.age = "{} day old".format(delta.days)
            elif delta.days == 0:
                lead.age = "{} day old (created/converted today)".format(delta.days)
            else:
                lead.age = "{} days old".format(delta.days)
    

    @api.depends('campaign_id', 'unsubscribed_campaign_id')
    def _compute_gdpr(self):
        for record in self:
            if record.campaign_id and not record.unsubscribed_campaign_id:
                record.gdpr_status = 'in'
            elif record.unsubscribed_campaign_id:
                record.gdpr_status = 'out'
            else:
                record.gdpr_status = 'undefined'

    #if we change the partner_id, then we clean the ref to trigger a new creation at save
    @api.onchange('partner_id')
    def _clear_ref(self):
        for lead in self:
            lead.internal_ref = False
            
    
    @api.onchange('name')
    def _onchange_name(self):
        for lead in self:
            if lead.type == 'opportunity' and lead.internal_ref:
                lead.name = lead.build_opp_name(lead.internal_ref,lead.name)
    
    def _get_default_opted_in_date(self):
        for record in self:
            return record.create_date

    
    """@api.onchange('partner_id','country_id')
    def _change_am(self):
        for lead in self:
            lead.user_id = lead.guess_am()"""
    
    """@api.depends('partner_id','type')
    def _compute_internal_ref(self):
        for lead in self:
            if lead.partner_id and lead.type=='opportunity': #we compute a ref only for opportunities, not lead
                if not lead.partner_id.altname:
                    _logger.warning("Please document ALTNAME for the client {}".format(lead.partner_id.name))
                else:
                    next_index = lead.partner_id.core_process_index+1 or 1
                    _logger.info("_compute_internal_ref: Core Process increment for {} from {} to {}".format(lead.partner_id.name,lead.partner_id.core_process_index,next_index))
                    #lead.partner_id.write({'core_process_index': next_index})
                    lead.internal_ref = "{}-{:03}".format(lead.partner_id.altname,next_index)
                    lead.name_to_internal_ref(False)"""
                    
    """ @api.onchange('internal_ref')
    def _set_internal_ref(self):
        for lead in self:
            #format checking
            try:
                ref_alt = lead.internal_ref[:-4]
                ref_index = int(lead.internal_ref[-3:])
                if ref_alt.upper() != lead.partner_id.altname.upper():
                    _logger.warning("ALTNAME MISMATCH:{} in company and {} in opportunity {}".format(lead.partner_id.altname.upper(),ref_alt.upper(),lead.name))
                    return
                    #lead.internal_ref = False
                
                if ref_index > lead.partner_id.core_process_index:
                    lead.partner_id.write({'core_process_index': ref_index})
                    _logger.info("_set_internal_ref: Core Process update for {} to {}".format(lead.partner_id.name,ref_index))

            except:
                _logger.warning("Bad Lead Reference syntax: {}".format(lead.internal_ref))
                #lead.internal_ref = False"""


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
    
    def build_opp_name(self,reference=False,name=False):
        try:
            #if the name already contains the ref
            offset = name.upper().find(reference.upper())
            if offset == -1 and reference:
                return "{} | {}".format(reference,name)
            else:
                return name

        except:
            _logger.info("Unable to extract ref from opp name {}".format(name))
            return name

    """def name_to_internal_ref(self,write_ref = False):
        for lead in self:
            if lead.type == 'opportunity':
                #we verify if the format is matching expectations
                try:
                    #if the name already contains the ref
                    offset = lead.name.upper().find(lead.partner_id.altname.upper())
                    if offset != -1:
                        index = int(lead.name[offset+len(lead.partner_id.altname)+1:offset+len(lead.partner_id.altname)+4])
                        lead.name = "{}-{:03}{}".format(lead.partner_id.altname.upper(),index,lead.name[offset+len(lead.partner_id.altname)+4:])
                        if write_ref:
                            lead.internal_ref = "{}-{:03}".format(lead.partner_id.altname.upper(),index)
                            _logger.info("Updated Lead Ref: {}".format(lead.internal_ref))

                    elif lead.internal_ref:
                        lead.name = "{} | {}".format(lead.internal_ref,lead.name)

                except:
                    _logger.info("Unable to extract ref from opp name {}".format(lead.name))"""


    @api.multi
    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        """ extract data from lead to create a partner
            :param name : furtur name of the partner
            :param is_company : True if the partner is a company
            :param parent_id : id of the parent partner (False if no parent)
            :returns res.partner record
        """
        data = super()._create_lead_partner_data(name, is_company, parent_id)
        data['country_group_id'] = self.country_group_id.id
        data['referent_id'] = self.referent_id.id
        data['functional_focus_id'] = self.functional_focus_id.id
        data['partner_seniority_id'] = self.partner_seniority_id.id
        data['industry_id'] = self.industry_id.id
        data['client_activity_ids'] = [(6, 0, self.client_activity_ids.ids)]
        data['client_product_ids'] = [(6, 0, self.client_product_ids.ids)]
        data['linkedin'] = self.linkedIn_url
        data['category_id'] = [(4, self.env.ref('vcls-contact.category_account').id, 0)]
        if is_company:
            data['altname'] = self.altname
        else:
            if self.contact_middlename:
                data.update({
                    "lastname2": self.contact_middlename,
                })
                if 'name' in data:
                    del data['name']
        return data

    @api.multi
    def _convert_opportunity_data(self, customer, team_id=False):
        """ Extract the data from a lead to create the opportunity
            :param customer : res.partner record
            :param team_id : identifier of the Sales Team to determine the stage
        """
        data = super()._convert_opportunity_data(customer, team_id)
        
        """#program integration
        if customer:
            isFirstOpportunity = True if len(self.env['crm.lead'].search([('partner_id','=',customer.id)])) < 0 else False
            if isFirstOpportunity :
                values = {'name': "Opportunity's program for client : {}".format(customer.altName),'client_id':customer.id}
                if customer.expert_id:
                    values = values.update({'leader_id':customer.expert_id}) 
                elif customer.user_id:
                    values = values.update({'leader_id':customer.user_id})
                    
                new_program = self.env['project.program'].create(values)
                data['program_id'] = new_program.id"""
        
        data['country_group_id'] = self.country_group_id.id
        data['referent_id'] = self.referent_id.id
        data['functional_focus_id'] = self.functional_focus_id.id
        data['partner_seniority_id'] = self.partner_seniority_id.id
        data['industry_id'] = self.industry_id.id
        data['client_activity_ids'] = [(6, 0, self.client_activity_ids.ids)]
        data['client_product_ids'] = [(6, 0, self.client_product_ids.ids)]
        data['product_category_id'] = self.product_category_id.id
        data['converted_date'] = datetime.datetime.now()
        data['linkedIn_url'] = self.linkedIn_url
        
        return data

    def _onchange_partner_id_values(self, partner_id):
        result = super(Leads, self)._onchange_partner_id_values(partner_id)
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id)
            result.update({
                "industry_id": partner.industry_id,
                "client_activity_ids": [(6, 0, partner.client_activity_ids.ids)],
                "client_product_ids": [(6, 0, partner.client_product_ids.ids)]
            })
            if not partner.is_company:
                result.update({
                    "contact_middlename": partner.lastname2,
                })
        return result
    
    @api.onchange('contact_name','contact_lastname','contact_middlename')
    def _compute_partner_name(self):
        for lead in self:
            if lead.contact_name and lead.contact_lastname and lead.contact_middlename:
                res = lead.contact_name + " " + lead.contact_middlename + " " + lead.contact_lastname
                lead.name = res
            elif lead.contact_name and lead.contact_lastname:
                res = lead.contact_name + " " + lead.contact_lastname
                lead.name = res
    
    
    
    def all_campaigns_pop_up(self):
        model_id = self.env['ir.model'].search([('model','=','crm.lead')], limit = 1)
        return {
            'name': 'All participated campaigns',
            'view_mode': 'tree',
            'target': 'new',
            'res_model': 'marketing.participant',
            'type': 'ir.actions.act_window',
            'domain': "[('model_id','=', {}),('res_id','=',{})]".format(model_id.id, self.id)
        }
    
    def create_contact_pop_up(self):
        result = self.env['crm.lead'].browse(self.id).handle_partner_assignation('create', False)
        return result.get(self.id)
    
    # Copy/Paste in order to redirect to right view (overriden)
    @api.multi
    def redirect_opportunity_view(self):
        self.ensure_one()
        # Get opportunity views
        form_view = self.env.ref('crm.crm_case_form_view_oppor')
        tree_view = self.env.ref('crm.crm_case_tree_view_oppor')
        return {
            'name': _('Opportunity'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'crm.lead',
            'domain': [('type', '=', 'opportunity')],
            'res_id': self.id,
            'view_id': False,
            'views': [
                (form_view.id, 'form'),
                (tree_view.id, 'tree'),
                (False, 'kanban'),
                (False, 'calendar'),
                (False, 'graph')
            ],
            'type': 'ir.actions.act_window',
            'context': {'default_type': 'opportunity'}
        }
    

    @api.onchange('stage_id')
    def _check_won_lost(self):
        if self.stage_id == self.env.ref('crm.stage_lead4'):
            if len(self.won_reasons) == 0:
                raise ValidationError(_("Please use the \"MARK WON\" button or select at least 1 reason."))
    
    risk_raised = fields.Boolean(default = False)

    def raise_go_nogo(self):
        for record in self:
            self.env['risk']._raise_risk(self.env.ref('vcls-crm.risk_go_nogo'), '{},{}'.format(record._name, record.id))
            record.risk_raised = True
            
    def open_related_risks(self):
        return {
            'name': 'All related risk(s)',
            'view_mode': 'tree',
            'target': 'new',
            'res_model': 'risk',
            'type': 'ir.actions.act_window',
            'domain': "[('resource','=', '{},{}')]".format(self._name, self.id)
        }
