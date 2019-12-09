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
        domain="[('parent_id.name','=','Operations')]",
        string='VCLS Activity',
    )

    deliverable_id = fields.Many2one(
        'product.deliverable',
        string='Deliverable',
    )
    vcls_type = fields.Selection([
        ('rate', 'Rate'),
        ('vcls_service', 'VCLS service'),
        ('subscription', 'Subscription'),
        ('invoice', 'Invoice'),
        ('expense', 'Expense'),
        ('project_supplier', 'Project supplier'),
        ('admin_supplier', 'Admin supplier'),
        ('other','Other'),
        ], string="Vcls type",
        compute='_get_vcls_type',default='other',store=True
    )

    @api.multi
    @api.depends('seniority_level_id','type','recurring_invoice','sale_ok','purchase_ok','can_be_expensed','service_policy','service_tracking')
    def _get_vcls_type(self):
        for product in self:

            if product.seniority_level_id:
                product.vcls_type = 'rate'
                continue

            if product.recurring_invoice:
                product.vcls_type = 'subscription'
                continue

            if product.name == 'Deposit':
                product.vcls_type = 'invoice'
                continue 

            if product.name.lower() == 'Communication Rate'.lower():
                product.vcls_type = 'expense'
                continue   
            
            if product.purchase_ok:
                if 'Suppliers' in product.name :
                    product.vcls_type = 'project_supplier'
                else:
                    product.vcls_type = 'admin_supplier'
                continue
            
            if product.can_be_expensed:
                product.vcls_type = "expense"
                continue

            if product.type == 'service' and product.sale_ok and not product.purchase_ok and not product.can_be_expensed and not product.recurring_invoice and product.service_policy=='delivered_manual':
                product.vcls_type = 'vcls_service'
                continue
               
            else:
                product.vcls_type = 'other'

            #_logger.info("VCLS TYPE {} - {}, {}, {}, {}, {}, {}".format(product.vcls_type,product.name, product.sale_ok,product.purchase_ok, product.can_be_expensed, product.recurring_invoice, product.service_policy))


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
            #_logger.info("Custom VCLS product search start with {} to filter with mode {}, business line {} and deliverable {}".format(len(products),business_mode,business_line,deliverable_id))
            
            if business_mode:
                has_deliver = False

                if business_mode == 'all':
                    has_deliver = True

                elif business_mode == 'services':
                    products = products.filtered(lambda p: (not p.can_be_expensed) and (not p.seniority_level_id))
                    has_deliver = True
                
                elif business_mode == 'rates':
                    products = products.filtered(lambda p: (not p.can_be_expensed) and (p.seniority_level_id))
                
                elif business_mode == 'subscriptions':
                    products = products.filtered(lambda p: p.recurring_invoice)
                    #_logger.info("SEARCH found {} for mode {}".format(len(products),business_mode))
                
                if deliverable_id and has_deliver:
                    products = products.filtered(lambda p: p.deliverable_id.id == deliverable_id)
                    #_logger.info("SEARCH found {} for product {}".format(len(products),deliverable_id))

                """elif business_mode == 't_and_m':
                    products = products.filtered(lambda p: (not p.can_be_expensed) or (p.seniority_level_id))
                """

                

            if business_line:
                bl_childs = self.env['product.category'].search([('id','child_of',business_line)])
                products = products.filtered(lambda p: (p.categ_id in bl_childs)) 
                #_logger.info("SEARCH found {} in {}".format(len(products),bl_childs.mapped('name')))

            
            
            return products.ids

        else:
            product_ids = super(Product, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
            return product_ids