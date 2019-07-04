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