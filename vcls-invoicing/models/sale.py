# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    
    _inherit = 'sale.order'

    risk_id = fields.Many2one('risk', string='Risk')

    po_id = fields.Many2one('invoicing.po', string ='Purchase Order')

    def action_risk(self):
        view_ids = [self.env.ref('vcls-risk.view_risk_tree').id,
                    self.env.ref('vcls-risk.view_risk_kanban').id, 
                    self.env.ref('vcls-risk.view_risk_form').id ]
        risk_id = self.risk_id

        return {
            'name': 'All Risks',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form',
            'view_ids': view_ids,
            'target': 'current',
            'res_model': 'risk',
            'type': 'ir.actions.act_window',
            'context': {'search_default_id': risk_id.id,},
        } 

    def check_risk(self):
        order_lines = self.order_line
        
        for line in order_lines:
            if not self.risk_id:
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
                                    self.risk_id = risk
                    elif self.company_id.id != self.env.ref('vcls-hr.company_VCFR').id:
                        risk_type = self.env.ref('vcls-invoicing.non_standard_company')
                        resource ='sale.order,' + str(self.id)
                        risk = self.env['risk'].search([('resource', '=', resource)])
                        if not risk:
                            risk = self.env['risk']._raise_risk(risk_type, resource).id
                            self.risk_id = risk
                except Exception:
                    pass
    
    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if 'order_line' in vals:
            self.check_risk()
        return result

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        if 'order_line' in vals:
            result.check_risk()
        return result