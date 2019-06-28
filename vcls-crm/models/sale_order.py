# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    product_category_id = fields.Many2one(
        'product.category',
        string = 'Business Line',
        domain = "[('is_business_line','=',True)]"
    )

    business_mode = fields.Selection([
        ('t_and_m', 'T&M'), 
        ('fixed_price', 'Fixed Price'), 
        ], default='t_and_m')

    deliverable_id = fields.Many2one(
        'product.deliverable',
        string="Deliverable"
    )

    @api.model
    def create(self, vals):

        #if related to an opportunity
        if 'opportunity_id' in vals:
            opp_id = vals.get('opportunity_id')
            opp = self.env['crm.lead'].browse(opp_id)
            if opp:
                #we look at other eventual quotations from the same opp
                prev_quote = self.sudo().with_context(active_test=False).search([('opportunity_id','=',opp_id)])
                if prev_quote:
                    vals['name']=opp.name.replace(opp.internal_ref,"{}.{}".format(opp.internal_ref,len(prev_quote)+1))
                else:
                    vals['name']=opp.name

        result = super(SaleOrder, self).create(vals)
        return result

class Product(models.Model):

    _inherit = 'product.product'
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        business_mode = self._context.get('business_mode')
        business_line = self._context.get('business_line')
        deliverable_id = self._context.get('deliverable_id')
        product_ids = super(Product, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
        products = self.browse(product_ids)
        if business_mode and business_line and deliverable_id:
            products = products.filtered(lambda p: business_line in p.categ_id.ids and deliverable_id in p.deliverable_id.ids)
            if business_mode == 'fixed_price':
                products = products.filtered(lambda p: p.invoice_policy == 'order' and p.expense_policy == 'sales_price')
            elif business_mode == 't_and_m':
                products = products.filtered(lambda p: p.invoice_policy == 'order' and p.expense_policy == 'no' and p.seniority_level_id)
        print(product_ids)
        return products.ids
        
