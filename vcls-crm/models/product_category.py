# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):

    _inherit = 'product.category'

    is_business_line = fields.Boolean(
        default = False,
    )