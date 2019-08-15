# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import math

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

    user_id = fields.Many2one(
        'res.users', 
        track_visibility='onchange', 
        domain=lambda self: [("groups_id", "=", self.env['res.groups'].search([('name','=', 'Account Manager')]).id)]
    )

    #We never use several projects per quotation, so we highlight the 1st of the list
    project_id = fields.Many2one(
        'project.project',
        string = 'Project Name',
        compute='_compute_project_id',
        store=True,
    )

    parent_id = fields.Many2one(
        'sale.order',
        string="Parent Quotation",
        copy=True,
    )
    
    internal_ref = fields.Char(
        string="Ref",
        store = True,
    )

    ###############
    # ORM METHODS #
    ###############

    @api.model
    def create(self, vals):
        _logger.info("NEW QUOTATION: {}".format(vals))
        #if related to an opportunity
        if 'opportunity_id' in vals:
            opp_id = vals.get('opportunity_id')
            opp = self.env['crm.lead'].browse(opp_id)
            if opp:
                #we look at other eventual quotations from the same opp
                prev_quote = self.sudo().with_context(active_test=False).search([('opportunity_id','=',opp_id)])
                if prev_quote:
                    # vals['name']=opp.name.replace(opp.internal_ref,"{}.{}".format(opp.internal_ref,len(prev_quote)+1))
                    vals['name'] = self.generate_name(opp.name, len(prev_quote)+1)
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
                        forecast.write({'start_date':vals['expected_start_date']})
       
       
        return super(SaleOrder, self).write(vals)

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('project_ids')
    def _compute_project_id(self):
        for so in self:
            if so.parent_id.project_id:
                so.project_id = so.parent_id.project_id
            elif so.project_ids:
                so.project_id = so.project_ids[0]


    ################
    # TOOL METHODS #
    ################
    
    @api.multi
    def upsell(self):
        for rec in self:
            new_order = rec.copy({'order_line': False,'parent_id':rec.id})
            #new_order.parent_id = rec

            """
            pending_section = None

            #we loop in source lines to copy rate ones only
            for line in rec.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                elif line.product_id.type == 'service' and \
                    line.product_id.service_policy == 'delivered_timesheet' and \
                    line.product_id.service_tracking in ('no', 'project_only'):
                    if pending_section:
                        pending_section.copy({'order_id': new_order.id})
                        pending_section = None
                    line.copy({'order_id': new_order.id,
                               'project_id': line.project_id.id,
                               'analytic_line_ids': [(6, 0, line.analytic_line_ids.ids)]})"""
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'target': 'current',
                'res_id': new_order.id,
            }

    """ @api.multi
    def copy_data(self, default=None):
        default['name']="I DO TEST"
        return super(SaleOrder, self).copy_data(default)"""

    @api.model
    def generate_name(self, name, number):
        map = {1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H', 9:'I', 10:'J',
                11:'K', 12:'L', 13:'M', 14:'O', 15:'P', 16:'Q', 17:'R', 18:'S', 19:'T',
                20:'U', 21:'V', 22:'W', 23:'X', 24:'Y', 26:'Z'}
        
        suffix = ""
        for i in range(math.ceil(number / 26)):
            key = number - i * 26
            suffix += "{}".format(map[key % 26])
        
        # need to add scope
        return name + suffix

