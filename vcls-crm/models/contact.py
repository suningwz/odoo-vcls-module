# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ContactExt(models.Model):

    _inherit = 'res.partner'
    
    ###  ###
    relation_ids = fields.Many2many(
        'res.partner.relation',
        readonly = True,
        string = 'Mapped Relations',
    )

    ### MARKETING FIELDS FOR TRACEABILITY ###
    
    #Marketing fields
    opted_in = fields.Boolean(
        string = 'Opted In',
    )

    opted_out = fields.Boolean(
        string = 'Opted Out',
    )

    vcls_contact_id = fields.Many2one(
        'res.users',
        string = "Initial Contact",
        domain = "[('employee','=',True)]",
    )

    default_currency_id = fields.Many2one(
        'res.currency',
        compute='_get_default_currency',
        inverse='_set_default_currency',
    )
    
    def _get_default_currency(self):
        ### handle the case where the user's company was created after the currency was set
        return self.property_product_pricelist.currency_id
    
    def _set_default_currency(self):
        self = self.sudo()
        pricelist = self.env['product.pricelist'].search([('company_id', '=', False), ('currency_id', '=', self.default_currency_id)], limit=1)
        if not pricelist:
            raise UserError(('Please define a company independent pricelist with currency %s') % self.default_currency_id.name)
        for company in self.env['res.company'].search():
            self.with_context(force_company=company.id).property_product_pricelist = pricelist