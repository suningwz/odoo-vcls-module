# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class Invoice(models.Model):
    _inherit = 'account.invoice'

    def _get_default_po_id(self):
        return self.env['sale.order'].search([('invoice_ids', 'in', [self.id])], limit=1).po_id

    po_id = fields.Many2one('invoicing.po', 
                            default = _get_default_po_id,  
                            string ='Purchase Order')
    
    def get_communication_amount(self):
        total_amount = 0
        lines = self.invoice_line_ids
        for line in lines:
            product = line.product_id
            if product:
                if product.id != self.env.ref('vcls-invoicing.product_communication_rate').id:
                    if product.communication_elligible:
                        total_amount += line.price_subtotal
                else:
                    line.unlink()
            else:
                total_amount += line.price_subtotal
        return total_amount
            
    
    @api.model
    def create(self, vals):
        ret = super(Invoice, self).create(vals)       
        partner = ret.partner_id
        if partner.communication_rate:
            total_amount = ret.get_communication_amount()
            if total_amount:
                line = self.env['account.invoice.line'].new()
                line.invoice_id = ret.id
                line.product_id = self.env.ref('vcls-invoicing.product_communication_rate').id
                line._onchange_product_id()
                line.price_unit = total_amount * partner.communication_rate / 100
                line.quantity = 1
                ret.with_context(communication_rate=True).invoice_line_ids += line
        return ret
    
    @api.multi
    def write(self, vals):
        ret = super(Invoice, self).write(vals)       
        for rec in self:
            partner = rec.partner_id
            if partner.communication_rate and not self.env.context.get('communication_rate'):
                total_amount = rec.get_communication_amount()
                if total_amount:
                    line = self.env['account.invoice.line'].new()
                    line.invoice_id = rec.id
                    line.product_id = self.env.ref('vcls-invoicing.product_communication_rate').id
                    line._onchange_product_id()
                    line.price_unit = total_amount * partner.communication_rate / 100
                    line.quantity = 1
                    rec.with_context(communication_rate=True).invoice_line_ids += line
        return ret
