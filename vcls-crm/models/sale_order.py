# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    product_category_id = fields.Many2one(
        'product.category',
        string = 'Business Line',
        domain = "[('parent_id','=',False)]"
    )

    name = fields.Char(readonly=False)
    default_name = fields.Char(readonly=True, compute='_compute_default_name', default="New")

    @api.onchange('partner_id')
    def _compute_default_name(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            if self.partner_id.altname:
                self.partner_id.nb_quotation += 1
                self.default_name = self.partner_id.altname + "-" + str(self.partner_id.nb_quotation) + "| "
                if self.opportunity_id.name:
                    self.default_name += self.opportunity_id.name
            else:
                raise UserError("Can you please document an ALTNAME for the related partner")
        return res


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.default_name == self.name:
            if self.partner_id:
                if self.partner_id.altname:
                    self.partner_id.nb_quotation += 1
                    self.name = self.partner_id.altname + "-" + str(self.partner_id.nb_quotation) + "| "
                    if self.opportunity_id.name:
                        self.name += self.opportunity_id.name
                else:
                    raise UserError("Can you please document an ALTNAME for the related partner")
        return res

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        if result.partner_id.altname:
            result.partner_id.nb_quotation += 1
            result.name = result.partner_id.altname + "-" + str(result.partner_id.nb_quotation) + "| "
            if result.opportunity_id.name:
                result.name += result.opportunity_id.name
        else:
            raise UserError("Can you please document an ALTNAME for the related partner")
        return result

    