from . import TranslatorSFLeads
from . import ETL_SF
from . import generalSync

import pytz
from simple_salesforce import Salesforce
from tzlocal import get_localzone
from datetime import datetime
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)


from odoo import models, fields, api

class SFLeadsSync(models.Model):
    _name = 'etl.salesforce.leads'
    _inherit = 'etl.sync.salesforce'

    def getSFTranslator(self, sfInstance):
        return TranslatorSFLeads.TranslatorSFLeads(sfInstance.getConnection())

    """ def getCronId(self, isFullUpdate):
        if isFullUpdate:
            return self.env.ref('vcls-etl.cron_etl_leads_full_Update').id
        else:
            return self.env.ref('vcls-etl.cron_etl_leads').id
    """
    def getSQLForKeys(self):
        sql =  'SELECT Id, LastModifiedDate '
        sql += 'FROM Lead'
        return sql
    
    def getSQLForRecord(self):
        sql = self.env.ref('vcls-etl.etl_sf_lead_query').value
        _logger.info(sql)
        return sql

    def getModifiedRecordsOdoo(self):
        return self.env['crm.lead'].search([('write_date','>', self.getStrLastRun()),('type','=','lead')])
    
    def getAllRecordsOdoo(self):
        return self.env['crm.lead'].search([('type','=','lead')])

    def getKeysFromOdoo(self):                
        return self.env['etl.sync.keys'].search([('odooModelName','=','crm.lead'),('externalObjName','=','Lead')])
    
    def getKeysToUpdateOdoo(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','crm.lead'),('externalObjName','=','Lead'),'|',('state','=','needCreateOdoo'),('state','=','needUpdateOdoo')])
    
    def getKeysToUpdateExternal(self):
        return self.env['etl.sync.keys'].search([('odooModelName','=','crm.lead'),('externalObjName','=','Lead'),'|',('state','=','needCreateExternal'),('state','=','needUpdateExternal')])

    
    def createKey(self, odooId, externalId):
        values = {'odooModelName':'crm.lead','externalObjName':'Lead'}
        if odooId:
            values.update({'odooId': odooId, 'state':'needCreateExternal'})
        elif externalId:
            values.update({'externalId':externalId, 'state':'needCreateOdoo'})
        self.env['etl.sync.keys'].create(values)

    def getExtModelName(self):
        return "Lead"
