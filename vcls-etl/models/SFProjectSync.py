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
        project_string = self.list_to_filter_string(self.mapped('project_sfid'))
        element_data = self._get_element_data(instance,project_string)
        project_data = self._get_project_data(instance,project_string)
        assignment_data = self._get_assignment_data(instance,project_string)

        proposal_string = self.list_to_filter_string(project_data,'KimbleOne__Proposal__c')
        proposal_data = self._get_proposal_data(instance,proposal_string)
        
        element_string = self.list_to_filter_string(element_data,'Id')
        milestone_data = self._get_milestone_data(instance,element_string)
        activity_data = self._get_activity_data(instance,element_string)
        annuity_data = self._get_annuity_data(instance,element_string)

        #Then we loop to process projects separately
        for project in self:
            if not project.so_ids: #no sale order yet
                to_create = project.prepare_so_data(project_data,proposal_data,element_data)
    
    ###

    def prepare_so_data(self,project_data,proposal_data,element_data):
        self.ensure_one()
        my_project = list(filter(lambda project: project['Id']==self.project_sfid,project_data))[0]
        my_proposal = list(filter(lambda proposal: proposal['Id']==my_project['KimbleOne__Proposal__c'],proposal_data))[0]
        
        #we get the source opportunity
        key = self.env['etl.sync.keys'].search([('externalId','=',my_proposal['KimbleOne__Opportunity__c']),('odooId','!=',False)],limit=1)
        if key:
            o_opp = self.env['crm.lead'].browse(int(key.odooId))
            _logger.info("Found Opp {} for project {} of proposal {}".format(o_opp.name,my_project['Name'],my_proposal['Id']))

        my_primary_elements = list(filter(lambda element: element['KimbleOne__OriginatingProposal__c']==my_project['KimbleOne__Proposal__c'],element_data))
        my_extention_elements = list(filter(lambda element: element['KimbleOne__OriginatingProposal__c']!=my_project['KimbleOne__Proposal__c'] and element['KimbleOne__DeliveryGroup__c']==my_project['Id'],element_data))
        
        for item in (self.split_elements(my_primary_elements) + self.split_elements(my_extention_elements)):
            _logger.info("Quotation to create: project {} proposal {} mode {}".format(my_project['KimbleOne__Reference__c'],item['proposal'],item['mode']))


    ###
    def split_elements(self,element_data):
        output = []
        proposals = []
        for element in element_data:
            combination = {}
            combination['proposal'] = element['KimbleOne__OriginatingProposal__c']
            prod_info = list(filter(lambda info: info['sf_id']==element['KimbleOne__Product__c'],SFProjectSync_constants.ELEMENTS_INFO))
            mode = prod_info[0]['mode'] if prod_info else False
            combination['mode'] = mode
            if (mode and (combination not in output)) or (combination['proposal'] not in proposals):
                output.append(combination)
                proposals.append(combination['proposal'])

        return output

    ###    
    def _get_element_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ELEMENT_DATA
        query += "WHERE KimbleOne__DeliveryGroup__c IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Elements".format(len(records)))
        
        return records

    def _get_project_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_PROJECT_DATA
        query += "WHERE Id IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Projects".format(len(records)))
        
        return records

    def _get_proposal_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_PROPOSAL_DATA
        query += "WHERE Id IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Proposals".format(len(records)))
        
        return records
    
    def _get_milestone_data(self,instance,filter_string = False):
        #we get only revenue milestones
        query = SFProjectSync_constants.SELECT_GET_MILESTONE_DATA
        query += "WHERE KimbleOne__DeliveryElement__c IN " + filter_string + " AND KimbleOne__MilestoneType__c='a3d3A0000004bNb'"
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Milestones".format(len(records)))
        
        return records
    
    def _get_assignment_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ASSIGNMENT_DATA
        query += "WHERE KimbleOne__DeliveryGroup__c IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Assignments".format(len(records)))
        
        return records
    
    def _get_activity_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ACTIVITY_DATA
        query += "WHERE KimbleOne__DeliveryElement__c IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Resourced Activities".format(len(records)))
        
        return records
    
    def _get_annuity_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ANNUITY_DATA
        query += "WHERE KimbleOne__DeliveryElement__c IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Annuities".format(len(records)))
        
        return records


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
    """def id_list_to_filter_string(self,list_in):
        stack = []
        for item in list_in:
            stack.append("\'{}\'".format(item))
        result = "({})".format(",".join(stack))
        return result"""
    
    def list_to_filter_string(self,list_in,key=False):
        stack = []
        for item in list_in:
            if key:
                stack.append("\'{}\'".format(item[key])) 
            else:
                stack.append("\'{}\'".format(item))  
        result = "({})".format(",".join(stack))
        return result
        
        

    



