# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

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

