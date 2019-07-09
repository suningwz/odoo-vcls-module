# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    risk_ids = fields.Many2many('risk', string='Risk')
    risk_score = fields.Integer(
        string='Risk Score',
        compute = '_compute_risk_score',
    )

    po_id = fields.Many2one('invoicing.po', string ='Purchase Order')

    def action_risk(self):
        view_ids = [self.env.ref('vcls-risk.view_risk_tree').id,
                    self.env.ref('vcls-risk.view_risk_kanban').id, 
                    self.env.ref('vcls-risk.view_risk_form').id ]
        
        resource ="sale.order,{}".format(self.id)

        return {
            'name': 'All Risks',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form',
            'view_ids': view_ids,
            'target': 'current',
            'res_model': 'risk',
            'type': 'ir.actions.act_window',
            'context': {'search_default_resouce':resource,},
        } 

    def check_risk(self):
        try:
            risk_company = self.env.ref('vcls-invoicing.non_standard_company')
            risk_rate = self.env.ref('vcls-invoicing.non_standard_rates')
        except:
            risk_company = False
            risk_rate = False

        for so in self:

            resource ="sale.order,{}".format(so.id)

            if so.company_id:
                if so.company_id != self.env.ref('vcls-hr.company_VCFR'):
                    existing = self.env['risk'].search([('resource', '=', resource),('risk_type_id','=',risk_company.id)])
                    if not existing:
                        so.risk_ids |= self.env['risk']._raise_risk(risk_company, resource)
            
            rates = so.order_line.filtered(lambda r: r.product_id.seniority_level_id)

            for rate in rates:
                std_price = rate.product_id.item_ids.filtered(lambda s: s.pricelist_id == so.pricelist_id)
                if std_price:
                    if rate.price_unit < std_price[0].fixed_price:
                        existing = self.env['risk'].search([('resource', '=', resource),('risk_type_id','=',risk_rate.id)])
                        if not existing:
                            so.risk_ids |= self.env['risk']._raise_risk(risk_rate, resource)
                        break

        def _compute_risk_score(self):
            for so in self:
                so.score = sum(so.risk_ids.mapped('score'))
                    
            

        """order_lines = self.order_line
        
        for line in order_lines:
            so_line_price = line.price_unit
            product_prices = line.product_id.item_ids

            try:
                if line.product_id.seniority_level_id:
                    for product_price in product_prices:
                        if product_price.pricelist_id == line.pricelist_id and product_price.fixed_price != so_line_price:
                            risk_type = self.env.ref('vcls-invoicing.non_standard_rates')
                            resource ='sale.order,' + str(self.id)
                            risk = self.env['risk'].search([('resource', '=', resource)])
                            if not risk:
                                risk = self.env['risk']._raise_risk(risk_type, resource).id
                                self.risk_ids = risk

                if self.company_id.id != self.env.ref('vcls-hr.company_VCFR').id:
                    risk_type = self.env.ref('vcls-invoicing.non_standard_company')
                    resource ='sale.order,' + str(self.id)
                    risk = self.env['risk'].search([('resource', '=', resource)])
                    if not risk:
                        risk = self.env['risk']._raise_risk(risk_type, resource).id
                        self.risk_ids = risk

            except Exception:
                pass"""
    
    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        self.check_risk()
        return result

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        result.check_risk()
        return result