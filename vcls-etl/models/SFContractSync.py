from . import TranslatorSFContract
from . import ETL_SF
from . import generalSync

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

class SFContractSync(models.Model):
    _name = 'etl.salesforce.contract'
    _inherit = 'etl.sync.salesforce'

    def getSFTranslator(self, sfInstance):
        return TranslatorSFContract.TranslatorSFContract(sfInstance.getConnection())

    def getSQLForKeys(self):
        sql =  'SELECT Id, LastModifiedDate '
        sql += 'FROM Contract '
        return sql
    
    def getSQLForRecord(self):
        sql = "Select Id, LastModifiedDate, Name, External_Contract_Name__c, AccountId, "
        sql+= "CompanySignedDate, CompanySignedId, ContractNumber, ContractTerm, Contract_End_Date__c, "
        sql+= "Contract_Update__c, Contract_URL__c, CurrencyIsoCode, CustomerSignedDate, "
        sql+= "CustomerSignedId, CustomerSignedTitle, EndDate,Link_to_Parent_Contract__c, "
        sql+= "OwnerId, Parent_Contract_Name__c, Parent_Contract_Type__c, "
        sql+= "Replaces_Supersedes__c, Type_of_Contract__c, VCLS_Status__c "
        sql+= "From Contract "
        
        return sql

    def getModifiedRecordsOdoo(self):
        return self.env['agreement'].search([('write_date','>', self.getStrLastRun()),('is_company','=',False),('is_internal','=',False)])

    def getAllRecordsOdoo(self):
        return self.env['agreement'].search([('is_company','=',False)])
        
    def getKeysFromOdoo(self):                
        return self.env['etl.sync.keys'].search([('odooModelName','=','agreement'),('externalObjName','=','Contract')])
    
    def getKeysToUpdateOdoo(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','agreement'),('externalObjName','=','Contract'),'|',('state','=','needCreateOdoo'),('state','=','needUpdateOdoo')])
    
    def getKeysToUpdateExternal(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','agreement'),('externalObjName','=','Contract'),'|',('state','=','needCreateExternal'),('state','=','needUpdateExternal')])

    def createKey(self, odooId, externalId):
        values = {'odooModelName':'agreement','externalObjName':'Contract'}
        if odooId:
            values.update({'odooId': odooId, 'state':'needCreateExternal'})
        elif externalId:
            values.update({'externalId':externalId, 'state':'needCreateOdoo'})
        self.env['etl.sync.keys'].create(values)
    
    def getExtModelName(self):
        return "Contract"