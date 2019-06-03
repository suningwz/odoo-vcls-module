from . import TranslatorSFContact
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

class SFContactSync(models.Model):
    _name = 'etl.salesforce.contact'
    _inherit = 'etl.sync.salesforce'

    def getSFTranslator(self, sfInstance):
        return TranslatorSFContact.TranslatorSFContact(sfInstance.getConnection())

    """def getCronId(self, isFullUpdate):
        if isFullUpdate:
            return self.env.ref('vcls-etl.cron_etl_contact_full_Update').id
        else:
            return self.env.ref('vcls-etl.cron_etl_contact').id
    """
    def getSQLForKeys(self):
        sql =  'SELECT C.Id, C.LastModifiedDate '
        sql += 'FROM Contact as C '
        sql += 'Where C.AccountId In ('
        sql +=  'SELECT A.Id '
        sql +=  'FROM Account as A '
        sql +=  'WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)'
        sql += ') '
        return sql
    
    def getSQLForRecord(self):
        sql =  'SELECT C.Id, C.Name, C.AccountId, C.Phone, C.Fax, '
        sql += 'C.OwnerId, C.LastModifiedDate, C.LinkedIn_Profile__c, '
        sql += 'C.Category__c, C.Supplier__c, Salutation, C.Email, '
        sql += 'C.Title, C.MobilePhone, C.MailingAddress, C.AccountWebsite__c, '
        sql += 'C.Description, C.MailingCountry, C.Inactive_Contact__c, C.CurrencyIsoCode, '
        sql += 'C.Opted_In__c, C.VCLS_Main_Contact__c, C.Unsubscribed_from_Marketing_Comms__c, '
        sql += 'C.VCLS_Initial_Contact__c '
        sql += 'FROM Contact as C '
        sql += 'Where C.AccountId In ('
        sql +=  'SELECT A.Id '
        sql +=  'FROM Account as A '
        sql +=  'WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)'
        sql += ') '
        return sql

    def getModifiedRecordsOdoo(self):
        return self.env['res.partner'].search([('write_date','>', self.getStrLastRun()),('is_company','=',False),('is_internal','=',False)])

    def getKeysFromOdoo(self):                
        return self.env['etl.sync.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','Contact')])
    
    def getKeysToUpdateOdoo(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','Contact'),'|',('state','=','needCreateOdoo'),('state','=','needUpdateOdoo')])
    
    def getKeysToUpdateExternal(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','Contact'),'|',('state','=','needCreateExternal'),('state','=','needUpdateExternal')])

    def createKey(self, odooId, externalId):
        values = {'odooModelName':'res.partner','externalObjName':'Contact'}
        if odooId:
            values.update({'odooId': odooId, 'state':'needCreateExternal'})
        elif externalId:
            values.update({'externalId':externalId, 'state':'needCreateOdoo'})
        self.env['etl.sync.keys'].create(values)
    
    def getExtModelName(self):
        return "Contact"