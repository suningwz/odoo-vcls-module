from . import ETL_SF
from . import generalSync
from . import SFProjectSync_constants
from . import SFProjectSync_mapping

import pytz
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
from tzlocal import get_localzone
from datetime import date
from datetime import datetime
from datetime import timedelta
import time
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    ts_migrated = fields.Boolean(
        default=False,
    )

    ts_max_id = fields.Integer(
        default = 0,
        readonly = True,
    )

class Subscription(models.Model):

    _inherit = 'sale.subscription'

    @api.multi
    def force_start_date(self):
        """
        This is used inparticular in automated migration in order to avoid the default dates not to be today()
        """
        for sub in self:
            sub.date_start = sub.date_start.replace(day=1)
            if sub.template_id.recurring_rule_type == 'monthly':
                sub.recurring_next_date = sub.recurring_next_date.replace(month=sub.date_start.month + sub.template_id.recurring_interval,day=1)
            elif sub.template_id.recurring_rule_type == 'yearly':
                sub.recurring_next_date = sub.recurring_next_date.replace(year=sub.date_start.year + sub.template_id.recurring_interval,day=1)
            else:
                sub.recurring_next_date = sub.date_start

    