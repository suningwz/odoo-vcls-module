# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from collections import OrderedDict
from odoo.tools import OrderedSet

from odoo.exceptions import UserError, ValidationError, Warning
import math

import logging
_logger = logging.getLogger(__name__)


class SaleReport(models.Model):

    _inherit = 'sale.report'

    expected_start_date = fields.Date(
        related = 'order_id.expected_start_date'
    )

    expected_end_date = fields.Date(
        related = 'order_id.expected_end_date'
    )