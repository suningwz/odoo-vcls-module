# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ExpertiseArea(models.Model):

    _name = 'expertise.area'

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char()

class ProjectSupplierType(models.Model):

    _name = 'project.supplier.type'

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char()

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

