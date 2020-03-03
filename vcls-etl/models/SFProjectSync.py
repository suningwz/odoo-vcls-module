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

#######
### WE EXETEND THE KEY MODEL
###
class ETLKey(models.Model):
    _inherit = 'etl.sync.keys' 

    state = fields.Selection(
        selection_add = [('map', 'MAP')],
    )
    name = fields.Char()
    search_value = fields.Char()
    odooId = fields.Char(
        readonly = False,
    )

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
        self._build_product_map(instance)
    
    def _build_company_map(self,instance=False):
        sf_model = 'KimbleOne__BusinessUnit__c'
        od_model = 'res.company'

        if not instance:
            return False
        
        query = """
            SELECT Id, Name FROM KimbleOne__BusinessUnit__c
        """
        records = instance.getConnection().query_all(query)['records']

        for rec in records:
            key = self.env['etl.sync.keys'].search([('externalObjName','=',sf_model),('externalId','=',rec['Id']),('odooModelName','=',od_model),('state','=','map')],limit=1)
            if not key:
                key = self.env['etl.sync.keys'].create({
                    'externalObjName':sf_model,
                    'externalId':rec['Id'],
                    'odooModelName':od_model,
                    'state':'map',
                    'name':rec['Name'],
                })

            if not key.odooId:
                found = self.env[od_model].search([('name','=ilike',rec['Name'])],limit=1)
                if found:
                    key.write({'odooId':str(found.id)})

        #_logger.info("{}\n{}".format(query,records))
    
    def _build_product_map(self,instance=False):
        sf_model = 'KimbleOne__Product__c'
        od_model = 'product.template'

        if not instance:
            return False
        
        query = """
            SELECT Id, Name FROM KimbleOne__Product__c
        """
        records = instance.getConnection().query_all(query)['records']
        s_query = """
            SELECT Activity__c FROM KimbleOne__DeliveryElement__c WHERE Automated_Migration__c = TRUE
        """
        search_values = instance.getConnection().query_all(s_query)['records']
        _logger.info("{}\n{}".format(s_query,search_values))
        search_values = self._get_unique_records(search_values,'Activity__c')
        _logger.info("{}\n{}".format(s_query,search_values))

        for product in records:
            for item in search_values:
                key = self.env['etl.sync.keys'].search([('externalObjName','=',sf_model),('externalId','=',product['Id']),('search_value','=',item),('odooModelName','=',od_model),('state','=','map')],limit=1)
                if not key:
                    key = self.env['etl.sync.keys'].create({
                        'externalObjName':sf_model,
                        'externalId':product['Id'],
                        'odooModelName':od_model,
                        'search_value':item if item != None else False,
                        'state':'map',
                        'name':product['Name'],
                    })

    def _test_maps(self,instance=False):
        if not instance:
            return False

        for key in self.env['etl.sync.keys'].with_context(active_test=False).search([('state','=','map'),('odooId','!=',False)]):
            try:
                record = self.env[key.odooModelName].browse(int(key.odooId))
            except:
                _logger.info("ETL BAD ODOO KEY {} {}".format(key.odooModelName,key.odooId))
                return False
        
        return True

    
    ####
    ## TOOL METHODS
    ###

    def _get_unique_records(self,records,key):
        result = []
        for rec in records:
            result.append(rec[key])
        return list(set(result))



