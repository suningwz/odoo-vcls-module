# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    product_category_id = fields.Many2one(
        'product.category',
        string = 'Business Line',
        domain = "[('is_business_line','=',True)]"
    )
    
    company_id = fields.Many2one(default=lambda self: self.env.ref('vcls-hr.company_VCFR'))

    business_mode = fields.Selection([
        #('t_and_m', 'T&M'), 
        #('fixed_price', 'Fixed Price'), 
        ('all', 'All'),
        ('services', 'Services'),
        ('rates', 'Rates'),
        ('subscriptions', 'Subscriptions'),
        ], default='all',
        string = "Product Type")

    deliverable_id = fields.Many2one(
        'product.deliverable',
        string="Deliverable"
    )
    expected_start_date = fields.Date()
    expected_end_date = fields.Date()

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
                #default expected_start_date and expected_end_date
                expected_start_date = opp.expected_start_date
                if expected_start_date:
                    vals['expected_start_date'] = expected_start_date
                    vals['expected_end_date'] = expected_start_date + relativedelta(months=+3)
                

        result = super(SaleOrder, self).create(vals)
        return result

    @api.model
    def write(self, vals):
        if 'expected_start_date' in vals:
            expected_start_date = fields.Date.from_string(vals['expected_start_date'])
            if self.expected_end_date and self.expected_start_date and expected_start_date:
                vals['expected_end_date'] = expected_start_date + (self.expected_end_date - self.expected_start_date)
            if self.tasks_ids:
                for task_id in self.tasks_ids:
                    forecasts = self.env['project.forecast'].search([('task_id','=',task_id.id)])
                    for forecast in forecasts:
                        forecast.write({'start_date' : vals['expected_start_date']})

        return super(SaleOrder, self).write(vals)

