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
        sql = 'SELECT Id, LastModifiedDate FROM Account ' + self.env.ref('vcls-etl.etl_sf_account_filter').value
        _logger.info(sql)
        return sql
    
    def getSQLForRecord(self):
        sql = self.env.ref('vcls-etl.etl_sf_account_query').value + ' ' + self.env.ref('vcls-etl.etl_sf_account_filter').value
        _logger.info(sql)
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