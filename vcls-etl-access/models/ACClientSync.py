from . import TranslatorACClient
from . import ETL_ACCESS
from . import generalSync
import logging
_logger = logging.getLogger(__name__)

from tzlocal import get_localzone
import pytz
from datetime import datetime

from odoo import exceptions, models, fields, api

class ACClientSync(models.Model):
    _name = 'etl.access.client'
    _inherit = 'etl.sync.access'

    def getSFTranslator(self, accessInstance):
        return TranslatorAccessClient.TranslatorAccessClient(accessInstance.getConnection())

    def getSQLForKeys(self):
        sql = 'SELECT ClientID FROM tblClient as A '
        _logger.info(sql)
        return sql
    
    def getSQLForRecord(self):
        sql = self.env.ref('vcls-etl.etl_access_tblClient_query').value
        _logger.info(sql)
        return sql 

    def getModifiedRecordsOdoo(self):
        return self.env['res.partner'].search([('write_date','>', self.getStrLastRun())])

    def getAllRecordsOdoo(self):
        return self.env['res.partner'].search([])

    def getKeysFromOdoo(self):                
        return self.env['etl.sync.access.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','tblClient')])
    
    def getKeysToUpdateOdoo(self):
        return self.env['etl.sync.access.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','tblClient'),'|',('state','=','needCreateOdoo'),('state','=','needUpdateOdoo')])
    
    def getKeysToUpdateExternal(self):
        return self.env['etl.sync.access.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','tblClient'),'|',('state','=','needCreateExternal'),('state','=','needUpdateExternal')])

    
    def createKey(self, odooId, externalId):
        values = {'odooModelName':'res.partner','externalObjName':'tblClient'}
        if odooId:
            values.update({'odooId': odooId, 'state':'needCreateExternal'})
        elif externalId:
            values.update({'externalId':externalId, 'state':'needCreateOdoo'})
        self.env['etl.sync.keys'].create(values)

    def getExtModelName(self):
        return "tblClient"