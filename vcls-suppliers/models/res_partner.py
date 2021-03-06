# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ExpertiseArea(models.Model):

    _name = 'expertise.area'
    _description = 'Used to search for specific project suppliers.'

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )

class ProjectSupplierType(models.Model):

    _name = 'project.supplier.type'
    _description = 'Defines contractual situation of the supplier.'

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )

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

    project_supplier_type_id = fields.Many2one(
        'project.supplier.type',
        string = "Project Supplier Type",
    )

    expertise_area_ids = fields.Many2many(
        'expertise.area',
        string="Area of Expertise",
    )

    user_skill_ids = fields.One2many(
        string='Skills',
        comodel_name='res.partner.skill',
        inverse_name='user_id',
    ) 

    def action_po(self):
        return {
            'name': 'Purchase Order',
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'current',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'context': {'search_default_partner_id': self.id},
        } 
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        supplier_search = self._context.get('supplier_search')

        #if we are in the context of a vcls custom search
        if supplier_search:
            expertise_ids = self._context.get('expertise_ids')[0][2]
            expertises = self.env['expertise.area'].browse(expertise_ids)

            partner_ids = super(ContactExt, self)._search(args, offset, None, order, count=count, access_rights_uid=access_rights_uid)
            partners = self.browse(partner_ids)

            #we filter according to the expertises
            if expertises:
                partners = partners.filtered(lambda p: expertises in p.expertise_area_ids)
            
            #if no one has been found,propose default one
            if len(partners)==0:
                try:
                    not_found = self.env.ref('vcls-suppliers.not_found_sup')
                    return not_found.id
                except:
                    pass
        
            return partners.ids
        
        else:
            partner_ids = super(ContactExt, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
            return partner_ids

