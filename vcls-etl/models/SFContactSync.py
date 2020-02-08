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
        sql =  'SELECT C.Id, C.LastModifiedDate ' + self.env.ref('vcls-etl.etl_sf_contact_filter').value
        _logger.info(sql)
        return sql
    
    def getSQLForRecord(self):
        sql = self.env.ref('vcls-etl.etl_sf_contact_query').value + ' ' + self.env.ref('vcls-etl.etl_sf_contact_filter').value
        _logger.info(sql)
        return sql

    def getModifiedRecordsOdoo(self):
        return self.env['res.partner'].search([('write_date','>', self.getStrLastRun()),('is_company','=',False),('is_internal','=',False)])

    def getAllRecordsOdoo(self):
        return self.env['res.partner'].search([('is_company','=',False)])
        
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