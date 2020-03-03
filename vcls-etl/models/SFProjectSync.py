from . import ETL_SF
from . import generalSync
from . import SFProjectSync_constants

import pytz
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
from tzlocal import get_localzone
from datetime import datetime
from datetime import timedelta
import time
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api

class SFProjectSync(models.Model):
    _name = 'etl.salesforce.project'
    _inherit = 'etl.sync.salesforce'

    project_sfid = fields.Char()
    project_sfname = fields.Char()
    project_sfref = fields.Char()
    project_odid = fields.Integer()
    project_odname = fields.Char()
    project_odref = fields.Char()
    migration_status = fields.Selection(
        [
            ('todo', 'ToDo'),
            ('so', 'Sale Order'),
            ('structure', 'Structure'),
            ('ts', 'Timesheets'),
            ('complete', 'Complete'),
        ],
        default = 'todo', 
    )


    @api.model
    def build_maps(self):
        instance = self.getSFInstance()
        self._build_company_map(instance)
    
    def _build_company_map(self,instance=False):
        if not instance:
            return False
        
        query = """
            SELECT Id, Name FROM KimbleOne__BusinessUnit__c
        """
        records = instance.getConnection().query_all(query)['records']

        _logger.info("{}\n{}".format(query,records))


