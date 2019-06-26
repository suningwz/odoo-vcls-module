from . import TranslatorSFOpportunity
from . import ETL_SF
from . import generalSync

import pytz
from simple_salesforce import Salesforce
from tzlocal import get_localzone
from datetime import datetime
from datetime import timedelta

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class SFOpportunitySync(models.Model):
    _name = 'etl.salesforce.opportunity'
    _inherit = 'etl.sync.salesforce'

    def getSFTranslator(self, sfInstance):
        return TranslatorSFOpportunity.TranslatorSFOpportunity(sfInstance.getConnection())

    """ def getCronId(self, isFullUpdate):
        if isFullUpdate:
            return self.env.ref('vcls-etl.cron_etl_contact_full_Update').id
        else:
            return self.env.ref('vcls-etl.cron_etl_contact').id
    """
    def getSQLForKeys(self):
        sql =  'SELECT O.Id, O.LastModifiedDate '
        sql += 'FROM Opportunity as O '
        sql += 'Where O.AccountId In ('
        sql +=  'SELECT A.Id '
        sql +=  'FROM Account as A '
        sql +=  'WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)'
        sql += ')'

        sql = """
            SELECT O.Id, O.LastModifiedDate FROM Opportunity as O 
            WHERE O.AccountId In (
                SELECT A.Id FROM Account as A 
                WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)
                )
        """
        return sql
    
    def getSQLForRecord(self):
        sql =  'SELECT O.Id, O.Name, O.AccountId, O.StageName, O.Therapeutic_Area__c, '
        sql += 'O.OwnerId, O.LastModifiedDate, O.ExpectedRevenue, O.Reasons_Lost_Comments__c, O.Probability, O.CloseDate, O.Deadline_for_Sending_Proposal__c, O.LeadSource, '
        sql += 'O.Description, O.Client_Product_Description__c, O.CurrencyIsoCode, O.Product_Category__c, O.Amount, O.Geographic_Area__c, O.VCLS_Activities__c,Project_start_date__c '
        sql += 'FROM Opportunity as O '
        sql += 'Where O.AccountId In ('
        sql +=  'SELECT A.Id '
        sql +=  'FROM Account as A '
        sql +=  'WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)'
        sql += ') '
        
        return sql

    def getModifiedRecordsOdoo(self):
        return self.env['crm.lead'].search([('write_date','>', self.getStrLastRun()),('type','=','opportunity')])
    
    def getAllRecordsOdoo(self):
        return self.env['crm.lead'].search([('type','=','opportunity')])

    def getKeysFromOdoo(self):                
        return self.env['etl.sync.keys'].search([('odooModelName','=','crm.lead'),('externalObjName','=','Opportunity')])
    
    def getKeysToUpdateOdoo(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','crm.lead'),('externalObjName','=','Opportunity'),'|',('state','=','needCreateOdoo'),('state','=','needUpdateOdoo')])
    
    def getKeysToUpdateExternal(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','crm.lead'),('externalObjName','=','Opportunity'),'|',('state','=','needCreateExternal'),('state','=','needUpdateExternal')])

    
    def createKey(self, odooId, externalId):
        values = {'odooModelName':'crm.lead','externalObjName':'Opportunity'}
        if odooId:
            values.update({'odooId': odooId, 'state':'needCreateExternal'})
        elif externalId:
            values.update({'externalId':externalId, 'state':'needCreateOdoo'})
        self.env['etl.sync.keys'].create(values)

    def getExtModelName(self):
        return "Opportunity"