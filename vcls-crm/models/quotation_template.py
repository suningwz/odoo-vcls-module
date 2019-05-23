# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class QuotationTemplate(models.Model):

    _inherit = 'sale.order.template'

class QuotationTemplateLine(models.Model):

    _inherit = 'sale.order.template.line'
