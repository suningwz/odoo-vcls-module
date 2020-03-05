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

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def prepare_lines_data(self,elements=False):
        pass