# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    risk_ids = fields.Many2many('risk', string='Risk')

    def action_risk(self):
        view_id = self.env.ref('vcls-risk.view_risk_tree').id
        risk_ids = self.risk_ids

        print(risk_ids)
        return {
            'name': 'All Risks',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view_id,
            'target': 'current',
            'res_model': 'risk',
            'type': 'ir.actions.act_window',
            'context': {'search_default_id': risk_ids.ids,},
        } 

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def create_risk(self):
        so_line_price = self.price_unit
        product_price = self.product_id.list_price

        if product_price != so_line_price:
            resource ='sale.order.line,'+str(self.id)
            risk = self.env['risk'].search([('resource', '=', resource)])
            if not risk:
                risk_type = self.env['risk.type'].create({'name': 'RiskTest', 'active': True, 'model_name': 'sale.order.line'})
                risk = self.env['risk'].create({'risk_type_id': risk_type.id, 'resource': resource}).id
                self.order_id.risk_ids = [(4, risk)]

        """ product_prices = self.product_id.pricelist_item_ids
        for product_price in product_prices:
            if product_price.fixed_price == so_line_price:
                risk_type = self.env['risk.type'].create({'name': 'RiskTest', 'active': True, 'model_name': 'sale.order.line'})
                risk = self.env['risk'].create({'risk_type_id': risk_type.id, })
                self.order_id.risk_ids = [(6, 0, risk.id)] """
        

    @api.multi
    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        print("write : ")
        print(result)
        self.create_risk()
        return result

    @api.model
    def create(self, vals):
        result = super(SaleOrderLine, self).create(vals)
        print("create : ")
        print(result)
        result.create_risk()
        return result