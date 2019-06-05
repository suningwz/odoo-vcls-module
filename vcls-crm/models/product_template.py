# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class Deliverable(models.Model):

    _name = 'product.deliverable'
    _description = 'VCLS Deliverable'

    name = fields.Char()
    active = fields.Boolean(
        default = True,
    )

    product_category_id = fields.Many2one(
        'product.category',
        string = 'Business Line',
        domain = "[('parent_id','=',False)]"
    )

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    #################
    # CUSTOM FIELDS #
    #################

    department_id = fields.Many2one(
        'hr.department',
        domain = "[('parent_id.name','=','Operations')]",
        string = 'VCLS Activity',
    )

    deliverable_id = fields.Many2one(
        'product.deliverable',
        string = 'Deliverable',
    )

    grouping_info = fields.Char(
        store = True,
        compute = '_compute_grouping_info',
    )

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('deliverable_id','seniority_level_id')
    def _compute_grouping_info(self):
        for prod in self:
            if prod.deliverable_id:
                prod.grouping_info = prod.deliverable_id.name
            elif prod.seniority_level_id:
                prod.grouping_info = prod.seniority_level_id.name
            else:
                prod.grouping_info = False 
