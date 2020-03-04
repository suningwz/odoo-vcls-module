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

    @api.model
    def test(self):
        instance = self.getSFInstance()
        projects = self.search([('migration_status','=','todo')])
        _logger.info("Processing {} Projects".format(projects.mapped('project_sfref')))
        projects.build_quotations(instance)
    
    @api.multi
    def build_quotations(self,instance):
        if not instance:
            return False

        #We get all the source data required for the projects in self
        project_string = self.id_list_to_filter_string(self.mapped('project_sfid'))
        element_data = self._get_element_data(instance,project_string)
        project_data = self._get_project_data(instance,project_string)

        proposal_string = self.key_to_filter_string(project_data[0],'KimbleOne__Proposal__c')
        proposal_data = self._get_proposal_data(instance,proposal_string)
        """
        element_string = self.key_to_filter_string(element_data,'Id')
        milestone_data = self._get_milestone_data(instance,element_string)
        """

        #Then we loop to process projects separately
    
    ###

    def _get_element_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ELEMENT_DATA
        query += "WHERE KimbleOne__DeliveryGroup__c IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Elements".format(len(records)))
        
        return [records]

    def _get_project_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_PROJECT_DATA
        query += "WHERE Id IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Projects".format(len(records)))
        
        return [records]

    def _get_proposal_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_PROPOSAL_DATA
        query += "WHERE Id IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Projects".format(len(records)))
        
        return [records]
    
    def _get_milestone_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_MILESTONE_DATA
        query += "WHERE Id IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Projects".format(len(records)))
        
        return [records]


    ######
    @api.model
    def _dev(self):
        instance = self.getSFInstance()
        self._get_time_entries(instance)
    

    def _get_time_entries(self,instance=False):
        
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
        self._build_milestone_type(instance)
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


    ####################
    ## TOOL METHODS
    ####################
    def id_list_to_filter_string(self,list_in):
        stack = []
        for item in list_in:
            stack.append("\'{}\'".format(item))
        
        result = "({})".format(",".join(stack))
        return result
    
    def key_to_filter_string(self,list_in,key):
        result = "("
        for item in list_in:
            _logger.info("{}".format(item))
            _logger.info("{}".format(item[key]))
            #result += ("\'{}\',".format(item[key]))

        #result = result[:-1]+")"   
        return False
        
        

    



