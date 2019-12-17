# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_product_employee = fields.Boolean(string="Employee")

class Product(models.Model):

    _inherit = 'product.product'
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        vcls_company = self._context.get('vcls_expense_company')
        vcls_project = self._context.get('vcls_project')

        #VCLS Mobility case
        if vcls_project:
            project = self.env['project.project'].browse(vcls_project)
            if project.name == 'Mobility Boulogne':
                _logger.info("MOBILITY {}".format(project.name))
                product_ids = super(Product, self)._search(args, offset, None, order, count=count, access_rights_uid=access_rights_uid)
                product_ids.filtered(lambda p: p.categ_id.name == 'Mobility Expenses')
                return product_ids
        
        #if we are in the context of a vcls custom search
        if vcls_company:
            _logger.info("COMPANY {}".format(vcls_company))
            product_ids = super(Product, self)._search(args, offset, None, order, count=count, access_rights_uid=access_rights_uid)
            products = self.browse(product_ids)
            products = products.filtered(lambda p: ((not p.company_id) or (p.company_id.id==vcls_company)) and (p.categ_id.name != 'Mobility Expenses'))
            return products.ids

        else:
            product_ids = super(Product, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
            return product_ids