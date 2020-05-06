# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import datetime
import traceback

from collections import Counter
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import format_date
from odoo.tools.safe_eval import safe_eval

from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"
    


class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"
    