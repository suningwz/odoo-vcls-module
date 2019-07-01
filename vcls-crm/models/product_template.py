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
        domain = "[('is_business_line','=',True)]"
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
    
class Product(models.Model):

    _inherit = 'product.product'
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        business_mode = self._context.get('business_mode')
        business_line = self._context.get('business_line')
        deliverable_id = self._context.get('deliverable_id')
        product_ids = super(Product, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
        products = self.browse(product_ids)

        if business_line:
            business_line_child_ids = self.env['product.category'].browse(business_line).child_id.ids
            if business_line_child_ids:
                products = products.filtered(lambda p: p.categ_id.ids in business_line_child_ids)
        if deliverable_id:
            products = products.filtered(lambda p: deliverable_id in p.deliverable_id.ids)
        if business_mode:
            #If Fixed Price, Show only products with invoicing policy based on milestones and a re-invoicing policy configured as sales price
            if business_mode == 'fixed_price':
                products = products.filtered(lambda p: p.invoice_policy == 'delivered_manual' and p.expense_policy == 'sales_price')
            #If T&M, Show Services (i.e. milestones and re-invoicing = NO) and rates products (with a seniority level not null)
            elif business_mode == 't_and_m':
                products = products.filtered(lambda p: (p.invoice_policy == 'delivered_manual' and p.expense_policy == 'no') or (p.expense_policy == 'no' and p.seniority_level_id))
    
        return products.ids