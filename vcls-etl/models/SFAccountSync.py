from . import TranslatorSFAccount
from . import ETL_SF
from . import generalSync
import logging
_logger = logging.getLogger(__name__)

from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
from tzlocal import get_localzone
import pytz
from datetime import datetime

from odoo import exceptions, models, fields, api

class SFAccountSync(models.Model):
    _name = 'etl.salesforce.account'
    _inherit = 'etl.sync.salesforce'

    def getSFTranslator(self, sfInstance):

        return TranslatorSFAccount.TranslatorSFAccount(sfInstance.getConnection())

    def getSQLForKeys(self):
        sql = 'SELECT Id, LastModifiedDate FROM Account WHERE ((Supplier__c = True or Is_supplier__c = True) or (Project_Controller__c != null and VCLS_Alt_Name__c != null))'
        return sql
    
    def getSQLForRecord(self):
        sql = 'SELECT Id, Name, Supplier_Category__c, '
        sql += 'Supplier_Status__c, Account_Level__c, LastModifiedDate, '
        sql += 'BillingCountry, BillingState, BillingAddress, BillingStreet, '
        sql += 'Phone, Fax, Area_of_expertise__c, Sharepoint_Folder__c, '
        #sql += 'Phone, Fax, Area_of_expertise__c, Sharepoint_Folder__c, Sharepoint_ID__c, '
        sql += 'Supplier_Description__c, Key_Information__c, Project_Assistant__c, '
        sql += 'Supplier_Selection_Form_completed__c, Website, '
        sql += 'Create_Sharepoint_Folder__c, OwnerId, Is_supplier__c, VCLS_Main_Contact__c, '
        sql += 'Supplier__c, Type, Project_Controller__c, VCLS_Alt_Name__c,  '
        sql += 'Supplier_Project__c, Activity__c, Product_Type__c, Industry, KimbleOne__InvoicingCurrencyIsoCode__c, Invoice_Administrator__c '
        sql += 'FROM Account '
        sql += 'WHERE ((Supplier__c = True or Is_supplier__c = True) or (Project_Controller__c != null and VCLS_Alt_Name__c != null)) '
        return sql

    def getModifiedRecordsOdoo(self):
        return self.env['res.partner'].search([('write_date','>', self.getStrLastRun()),('is_company','=',True),('is_internal','=',False)])

    def getAllRecordsOdoo(self):
        return self.env['res.partner'].search([('is_company','=',True)])

    def getKeysFromOdoo(self):                
        return self.env['etl.sync.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','Account')])
    
    def getKeysToUpdateOdoo(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','Account'),'|',('state','=','needCreateOdoo'),('state','=','needUpdateOdoo')])
    
    def getKeysToUpdateExternal(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','Account'),'|',('state','=','needCreateExternal'),('state','=','needUpdateExternal')])

    
    def createKey(self, odooId, externalId):
        values = {'odooModelName':'res.partner','externalObjName':'Account'}
        if odooId:
            values.update({'odooId': odooId, 'state':'needCreateExternal'})
        elif externalId:
            values.update({'externalId':externalId, 'state':'needCreateOdoo'})
        self.env['etl.sync.keys'].create(values)

    def getExtModelName(self):
        return "Account"