from . import TranslatorSFCampaign
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

class SFCampaignSync(models.Model):
    _name = 'etl.salesforce.campaign'
    _inherit = 'etl.sync.salesforce'

    def getSFTranslator(self, sfInstance):
        return TranslatorSFCampaign.TranslatorSFCampaign(sfInstance.getConnection())

    def getSQLForKeys(self):
        sql = 'SELECT Id, LastModifiedDate FROM Campaign as A ' + self.env.ref('vcls-etl.etl_sf_campaign_filter').value
        _logger.info(sql)
        return sql
    
    def getSQLForRecord(self):
        sql = self.env.ref('vcls-etl.etl_sf_campaign_query').value + ' ' + self.env.ref('vcls-etl.etl_sf_campaign_filter').value
        _logger.info(sql)
        return sql 

    def getModifiedRecordsOdoo(self):
        return self.env['project.task'].search([('write_date','>', self.getStrLastRun())])

    def getAllRecordsOdoo(self):
        return self.env['project.task'].search([])

    def getKeysFromOdoo(self):                
        return self.env['etl.sync.keys'].search([('odooModelName','=','project.task'),('externalObjName','=','Campaign')])
    
    def getKeysToUpdateOdoo(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','project.task'),('externalObjName','=','Campaign'),'|',('state','=','needCreateOdoo'),('state','=','needUpdateOdoo')])
    
    def getKeysToUpdateExternal(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','project.task'),('externalObjName','=','Campaign'),'|',('state','=','needCreateExternal'),('state','=','needUpdateExternal')])

    
    def createKey(self, odooId, externalId):
        values = {'odooModelName':'project.task','externalObjName':'Campaign'}
        if odooId:
            values.update({'odooId': odooId, 'state':'needCreateExternal'})
        elif externalId:
            values.update({'externalId':externalId, 'state':'needCreateOdoo'})
        self.env['etl.sync.keys'].create(values)

    def getExtModelName(self):
        return "Campaign"