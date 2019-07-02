# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

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
        vcls_search = self._context.get('vcls_search')

        #if we are in the context of a vcls custom search
        if vcls_search:
            business_mode = self._context.get('business_mode')
            business_line = self._context.get('business_line')
            deliverable_id = self._context.get('deliverable_id')

            product_ids = super(Product, self)._search(args, offset, None, order, count=count, access_rights_uid=access_rights_uid)
            products = self.browse(product_ids)
            _logger.info("Custom VCLS product search start with {} to filter with mode {}, business line {} and deliverable {}".format(len(products),business_mode,business_line,deliverable_id))
            
            if business_mode:
                #If Fixed Price, Show only products with invoicing policy based on milestones and a re-invoicing policy configured as sales price
                if business_mode == 'fixed_price':
                    pass
                    #products = products.filtered(lambda p: p.invoice_policy == 'delivered_manual' and p.expense_policy == 'sales_price')
                #If T&M, Show Services (i.e. milestones and re-invoicing = NO) and rates products (with a seniority level not null)
                elif business_mode == 't_and_m':
                    products = products.filtered(lambda p: (not p.can_be_expensed) or (p.seniority_level_id))
                
                elif business_mode == 'subscriptions':
                    products = products.filtered(lambda p: p.recurring_invoice)
                
                _logger.info("SEARCH found {} for mode {}".format(len(products),business_mode))

            if business_line:
                bl_childs = self.env['product.category'].search([('id','child_of',business_line)])
                products = products.filtered(lambda p: p.categ_id in bl_childs)
                _logger.info("SEARCH found {} in {}".format(len(products),bl_childs.mapped('name')))

            if deliverable_id:
                products = products.filtered(lambda p: p.deliverable_id.id == deliverable_id)
                _logger.info("SEARCH found {} for product {}".format(len(products),deliverable_id))
            
            return products.ids

        else:
            product_ids = super(Product, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
            return product_ids



        """
        business_mode = self._context.get('business_mode')
        business_line = self._context.get('business_line')
        deliverable_id = self._context.get('deliverable_id')
        _logger.info("SEARCH context: {} {} {}".format(business_mode,business_line,deliverable_id))
        product_ids = super(Product, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
        products = self.browse(product_ids)
        _logger.info("SEARCH  args {} ".format(args))
        _logger.info("SEARCH found super: limit {} - found {} ".format(limit,len(products)))

        if business_line:
            bl_childs = self.env['product.category'].search([('id','child_of',business_line)])
            _logger.info("SEARCH BL cat: {} ".format(bl_childs.mapped('name')))
            products = products.filtered(lambda p: p.categ_id in bl_childs)

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
        """