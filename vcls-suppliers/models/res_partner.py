# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ProjectSupplierType(models.Model):

    _name = 'project.supplier.type'

    active = fields.Boolean()
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

