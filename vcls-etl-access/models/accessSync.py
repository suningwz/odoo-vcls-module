from . import ETL_ACCESS
from . import generalSync

import pytz
from tzlocal import get_localzone
from datetime import datetime
from datetime import timedelta
import time
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api

class accessSync(models.Model):
    _name = 'etl.sync.access'
    _inherit = 'etl.sync.mixin'

    def getAccessInstance(self):
        return ETL_ACCESS.ETL_ACCESS.getInstance()

    def getAccessTranslator(self, sfInstance):
        return "This stored de Translator"

    def getCronId(self, isFullUpdate):
        return "This store the cronId needed to be relaunch"
    
    def getSQLForKeys(self):
        return "This store the sql query needed for get keys"
    
    def getSQLForRecord(self):
        return "This store the sql query needed for get Salesforce Record"

    def getModifiedRecordsOdoo(self):
        return "This return the modified record from Odoo"

    def getAllRecordsOdoo(self):
        return "This return record from Odoo"

    def getKeysFromOdoo(self):
        return "This return the keys from Odoo"
    
    def getKeysToUpdateOdoo(self):
        return "This return the keys from Odoo when state is needUpdateOdoo or needCreateOdoo"

    def getKeysToUpdateExternal(self):
        return "This return the keys from Odoo when state is needUpdateExteral or needCreateExternal"
    
    def createKey(self,odooId,externalId):
        return "This will create a new key in etl.sync.keys"

    def getExtModelName(self):
        return "This return the model name of external"
    
    @api.model
    def access_process_keys(self,batch_size=False,loop=True,duration=9):
        keys = self.env['etl.sync.access.keys'].search([('state','not in',['upToDate','postponed'])]).mapped('priority')

        self.env.user.context_data_integration = True

        timestamp_end = datetime.now() + timedelta(minutes=duration) - timedelta(seconds=10)
        loop_cron = loop

        accessInstance = self.getAccessInstance()

        if keys:
            template = keys[0]
            _logger.info("ETL | Found {} {} keys {}".format(len(keys),template.externalObjName,template.state))
            #we initiate a sync object
            sync = self.env['etl.access.{}'.format(template.externalObjName.lower())]
            translator = sync.getAccessTranslator(accessInstance)
            counter = 0

            #get SF records
            query_id = "vcls-etl.etl_access_{}_query".format(template.externalObjName.lower())
            sql = self.env.ref(query_id).value
            records = accessInstance.getConnection().execute(sql)
            if records:
                _logger.info("ETL |  {} returned {} records from ACCESS".format(sql,len(records)))
                #we start the processing loop
                for access_rec in records:
                    if datetime.now()>timestamp_end:
                        break
                    else:
                        #grab the related key if in to_process
                        key = keys.filtered(lambda p: p.externalId == access_rec['ClientId'])
                        if key:
                            counter += 1
                            attributes = translator.translateToOdoo(access_rec, sync, accessInstance)
                            if not attributes:
                                key[0].write({'state':'postponed','priority':0})
                                _logger.info("ETL | Missing Mandatory info to process key {} - {}".format(key[0].externalObjName,key[0].externalId))
                                continue

                            #UPDATE Case
                            if key[0].state == 'needUpdateOdoo':
                                #we catch the existing record
                                o_rec = self.env[key[0].odooModelName].with_context(active_test=False).search([('id','=',key[0].odooId)],limit=1)
                                if o_rec:
                                    o_rec.with_context(tracking_disable=1).write(attributes)
                                    key[0].write({'state':'upToDate','priority':0})
                                    _logger.info("ETL | Record Updated {}/{} | {} | {}".format(counter,len(keys),key[0].externalObjName,attributes.get('log_info')))
                                else:
                                    key[0].write({'state':'upToDate','priority':0})
                                    _logger.info("ETL | Missed Update - Odoo record not found {}/{} | {} | {}".format(counter,len(keys),key[0].odooModelName,key[0].odooId))
                            
                            #CREATE Case
                            elif key[0].state == 'needCreateOdoo':
                                odoo_id = self.env[key[0].odooModelName].with_context(tracking_disable=1).create(attributes).id
                                key[0].write({'state':'upToDate','odooId':odoo_id,'priority':0})
                                #key[0].write({'state':'upToDate','priority':0})
                                _logger.info("ETL | Record Created {}/{} | {} | {}".format(counter,len(keys),key[0].externalObjName,attributes.get('log_info')))

                            else:
                                _logger.info("ETL | Non-managed key state {} | {}".format(key[0].id,key[0].state))
                        
            if loop_cron:
                cron = self.env.ref('vcls-etl.cron_relaunch')
                cron.write({
                    'active': True,
                    'nextcall': datetime.now() + timedelta(seconds=30),
                    'numbercall': 1,
                })
                _logger.info("ETL | CRON renewed")
            self.env.user.context_data_integration = False