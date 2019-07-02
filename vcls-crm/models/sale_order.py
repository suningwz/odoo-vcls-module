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
        ('subscriptions', 'Subscriptions'),
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
        
