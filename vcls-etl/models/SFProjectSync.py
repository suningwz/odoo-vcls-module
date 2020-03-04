from . import ETL_SF
from . import generalSync
from . import SFProjectSync_constants
from . import SFProjectSync_mapping

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
    #_name = 'etl.salesforce.project'
    _inherit = 'etl.sync.salesforce'

    project_sfid = fields.Char()
    project_sfname = fields.Char()
    project_sfref = fields.Char()
    so_ids = fields.Many2many(
        'sale.order',
        readonly = True,
    )
    project_ids = fields.Many2many(
        'project.project',
        readonly = True,
    )
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

    ####################
    ## MIGRATION METHODS
    ####################
    @api.model
    def initiate(self):
        instance = self.getSFInstance()

        query = """
        SELECT Id, Name, KimbleOne__Reference__c, Activity__c  
        FROM KimbleOne__DeliveryGroup__c 
        WHERE Automated_Migration__c = TRUE
        """
        records = instance.getConnection().query_all(query)['records']
        for rec in records:
            existing = self.search([('project_sfid','=',rec['Id'])],limit=1)
            if not existing:
                self.create({
                    'project_sfid': rec['Id'],
                    'project_sfname': rec['Name'],
                    'project_sfref': rec['KimbleOne__Reference__c'],
                })

        migrations = self.search([])
        for project in migrations:
            _logger.info("PROJECT MIGRATION STATUS | {} | {} | {}".format(project.project_sfref,project.project_sfname,project.migration_status))

    
    
    @api.multi
    def build_quotations(self,instance):
        element_data = self._get_element_data(instance)
        project_data = self._get_project_data(instance)
        


    def _get_element_data(self,instance):
        return []

    def _get_project_data(self,instance):
        return []




    ######
    @api.model
    def _dev(self):
        instance = self.getSFInstance()
        self._get_time_entries(instance)
    

    def _get_time_entries(self,instance=False):
        
        if not instance:
            return False
        
        query = """ 
            SELECT 
                Id,
                KimbleOne__DeliveryElement__c,
                KimbleOne__Category1__c,
                KimbleOne__Category2__c,
                KimbleOne__Category3__c,
                KimbleOne__Category4__c,
                KimbleOne__Notes__c,

                KimbleOne__InvoiceItemStatus__c,
                
                KimbleOne__TimePeriod__c,
                KimbleOne__Resource__c,
                KimbleOne__InvoicingCurrencyEntryRevenue__c,
                KimbleOne__EntryUnits__c,
                KimbleOne__ActivityAssignment__c,
                VCLS_Status__c
            FROM KimbleOne__TimeEntry__c
            WHERE KimbleOne__DeliveryElement__c IN ('a1U0Y00000BexAu','a1U0Y00000BexB4')
            AND VCLS_Status__c IN ('Billable - Draft','Billable - ReadyForApproval','Billable - Approved')
            """
            
            
        records = instance.getConnection().query_all(query)['records']
        for rec in records:
            _logger.info("{}\n{}".format(query,rec))
            break
        _logger.info("FOUND TIME ENTRIES {}".format(len(records)))



    ####################
    ## MAPPING METHODS
    ####################
    @api.model
    def build_reference_data(self):
        instance = self.getSFInstance()
        self._build_invoice_item_status(instance)
        self._build_time_periods(instance)

    @api.model
    def build_maps(self):
        instance = self.getSFInstance()
        self._build_company_map(instance)
        self._build_product_map(instance)
        self._build_rate_map(instance)
        self._build_user_map(instance)
        self._build_activity_map(instance)
        self._build_resources_map(instance)
        self._test_maps(instance)

    



