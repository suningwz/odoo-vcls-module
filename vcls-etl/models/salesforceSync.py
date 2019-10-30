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

class salesforceSync(models.Model):
    _name = 'etl.sync.salesforce'
    _inherit = 'etl.sync.mixin'

    def getSFInstance(self):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        return ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)

    def getSFTranslator(self, sfInstance):
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

    def run(self, isFullUpdate, createInOdoo, updateInOdoo, createRevert, updateRevert, nbMaxRecords):
        # run the ETL
        sfInstance = self.getSFInstance()
        #_logger.info(" SF Instance {}".format(sfInstance))
        translator = self.getSFTranslator(sfInstance)
        _logger.info(" TRANSLATOR {}".format(translator))
        #cronId = self.getCronId(isFullUpdate)

        #initialised the SfSync Object
        SF = self.env[self._name].search([], limit = 1)
        if not SF:
            SF = self.env[self._name].create({})
        
        #Update the context to execute vcls-rdd override
        self.env.user.context_data_integration = True

        #boolean for batch
        SF.updateKeyTable(sfInstance, isFullUpdate)

        #if isFinished :
   
        print('Updated key table done')
        _logger.info('Updated key table done')
        
        if createInOdoo or updateInOdoo:
            SF.updateOdooInstance(translator,sfInstance, createInOdoo, updateInOdoo,nbMaxRecords)
        
        print('Updated odoo instance done')
        _logger.info('Updated odoo instance done')
        
        if createRevert or updateRevert:
            SF.updateExternalInstance(translator,sfInstance, createRevert, updateRevert, nbMaxRecords)
        
        print('Updated sf instance done')
        _logger.info('Updated sf instance done')

        print('ETL IS FINISHED')
        _logger.info('ETL IS FINISHED')

        #Update the context back
        self.env.user.context_data_integration = False
        
        SF.setNextRun()
            
    def updateKeyTable(self, externalInstance, isFullUpdate):
        keys = self.getKeysFromOdoo()
        idKeysExt = []
        idKeysOdoo = []

        sql = str(self.getSQLForKeys())
        allRecordExt = externalInstance.getConnection().query_all(sql)['records']
        allRecordOdoo = self.getAllRecordsOdoo()
        if not isFullUpdate:
            if 'WHERE' in sql: 
                sql += 'AND '
            else:
                sql += 'WHERE '
            sql += 'LastModifiedDate > ' + self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") 
        
        sql += ' ORDER BY Name'
        
        print('Execute QUERY: {}'.format(sql))
        _logger.info('Execute QUERY: {}'.format(sql))
        
        #working on keys that were not created
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']
        modifiedRecordsOdoo = self.getModifiedRecordsOdoo()
        lastRun = self.getStrLastRun()


        if keys:
            if not isFullUpdate:

                for key in keys:
                    for item in allRecordExt:
                        if key.externalId == item['Id']:
                            key.lastModifiedExternal = datetime.strptime(item['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")
                            
                            print('Update Key Table Set Date, ExternalId :{}'.format(key.externalId))
                            _logger.info('Update Key Table Set Date, ExternalId :{}'.format(key.externalId))
                    for item in allRecordOdoo:
                        if key.odooId == str(item.id):
                            key.lastModifiedOdoo = self.getLastUpdate(str(item.id))
                            print('Update Key Table Set Date, OdooId :{}'.format(key.odooId))
                            _logger.info('Update Key Table Set Date, OdooId :{}'.format(key.odooId))
                    if not key.lastModifiedExternal:
                        key.lastModifiedExternal = lastRun
                    if not key.lastModifiedOdoo:
                        key.lastModifiedOdoo = lastRun

            for key in keys:
                if key.externalId:
                    idKeysExt.append(key.externalId)
                if key.odooId:
                    idKeysOdoo.append(key.odooId)

                if isFullUpdate or key.lastModifiedOdoo > lastRun or key.lastModifiedExternal > lastRun:
                    if isFullUpdate or not self.isDateOdooAfterExternal(key.lastModifiedOdoo, key.lastModifiedExternal):
                        # Exist in Odoo & External
                        # External is more recent
                        if key.odooId:
                            key.setState('needUpdateOdoo')
                            print('Update Key Table needUpdateOdoo, ExternalId :{}'.format(key.externalId))
                            _logger.info('Update Key Table needUpdateOdoo, ExternalId :{}'.format(key.externalId))
                        else:
                            key.setState('needCreateOdoo')
                            print('Update Key Table needCreateOdoo, ExternalId :{}'.format(key.externalId))
                            _logger.info('Update Key Table needCreateOdoo, ExternalId :{}'.format(key.externalId))
                    else:
                        # Exist in Odoo & External
                        # Odoo is more recent
                        if key.externalId:
                            key.setState('needUpdateExternal')
                            print('Update Key Table needUpdateExternal, ExternalId :{}'.format(key.externalId))
                            _logger.info('Update Key Table needUpdateExternal, ExternalId :{}'.format(key.externalId))
                        else:
                            key.setState('needCreateExternal')
                            print('Update Key Table needCreateExternal, ExternalId :{}'.format(key.odooId))
                            _logger.info('Update Key Table needCreateExternal, ExternalId :{}'.format(key.odooId))
        
        idsListFromExt = []
        for record in modifiedRecordsExt:
            idsListFromExt.append(record['Id'])
        #this regroup keys that are present in Salesforce but were not created in Odoo yet

        keysToCreate = list(set(idsListFromExt) - set(idKeysExt))
        
        for key in keysToCreate:
            self.createKey(None,key)
            print('Update Key Table needCreateOdoo, ExternalId :{}'.format(key))
            _logger.info('Update Key Table needCreateOdoo, ExternalId :{}'.format(key))
        
        idsListFromOdoo = []
        for record in modifiedRecordsOdoo:
            idsListFromOdoo.append(str(record.id))
        #this regroup keys that are present in Odoo but were not created in Odoo yet        
        keysToCreate = list(set(idsListFromOdoo) - set(idKeysOdoo))
        
        for key in keysToCreate:
            self.createKey(key,None)
            print('Update Key Table needCreateExternal, OdooId : {}'.format(key))
            _logger.info('Update Key Table needCreateExternal, OdooId : {}'.format(key))    


    def updateOdooInstance(self, translator,externalInstance, createInOdoo, updateInOdoo, nbMaxRecords):
        sql = self.getSQLForRecord()
        sql += ' ORDER BY Name'
        Modifiedrecords = externalInstance.getConnection().query_all(sql)['records'] #All records
        keys = self.getKeysToUpdateOdoo()
        if not nbMaxRecords:
            nbMaxRecords = len(keys)
        i = 0
        if keys:
            for key in keys:
                item = None
                if i < nbMaxRecords:
                    if key.state == 'needUpdateOdoo' and updateInOdoo:
                        for record in Modifiedrecords:
                            if record['Id'] == key.externalId:
                                item = record
                        if item:
                            try:
                                odooAttributes = translator.translateToOdoo(item, self, externalInstance)
                                record = self.env[key.odooModelName].search([('id','=',key.odooId)], limit=1)
                                record.with_context(tracking_disable=1).write(odooAttributes)
                                print('Updated record in Odoo: {}'.format(item['Name']))
                                _logger.info('Updated record in Odoo: {}'.format(item['Name']))
                                key.state ='upToDate'
                                i += 1
                                print(str(i)+' / '+str(nbMaxRecords))
                                _logger.info(str(i)+' / '+str(nbMaxRecords))
                            except ValueError as error:
                                _logger.error(error)
                    elif key.state == 'needCreateOdoo' and createInOdoo:
                        for record in Modifiedrecords:
                            if record['Id'] == key.externalId:
                                item = record
                        if item:
                            odooAttributes = translator.translateToOdoo(item, self, externalInstance)
                            partner_id = self.env[key.odooModelName].with_context(tracking_disable=1).create(odooAttributes).id
                            print('Create new record in Odoo: {}'.format(item['Name']))
                            _logger.info('Create new record in Odoo: {}'.format(item['Name']))
                            key.odooId = partner_id
                            key.state ='upToDate'
                            i += 1
                            print(str(i)+' / '+str(nbMaxRecords))
                            _logger.info(str(i)+' / '+str(nbMaxRecords))
                
               

    def updateExternalInstance(self, translator, externalInstance, createRevert, updateRevert, nbMaxRecords):
        keysTable = self.getKeysToUpdateExternal()
        extModelName = self.getExtModelName()
        if not nbMaxRecords:
            nbMaxRecords = len(keysTable)
        i = 0
        if keysTable:
            for key in keysTable:
                item = None
                if i < nbMaxRecords:
                    if key.state == 'needUpdateExternal' and updateRevert:
                        try:   
                            item = self.env[key.odooModelName].search([('id','=',key.odooId)])
                            if item:
                                sfAttributes = translator.translateToSF(item, self)
                                sfInstance = externalInstance.getConnection()
                                sfRecord = getattr(sfInstance, extModelName).update(key.externalId,sfAttributes)
                                print('Update record in Salesforce: {}'.format(item.name))
                                _logger.info('Update record in Salesforce: {}'.format(item.name))
                                key.state ='upToDate'
                                i += 1
                                print(str(i)+' / '+str(nbMaxRecords))
                                _logger.info(str(i)+' / '+str(nbMaxRecords))
                        except SalesforceMalformedRequest as error:
                            print('Error : '+ item.name)
                            print(error.url)
                            print(error.content)
                            _logger.error(error.content)
                    elif key.state == 'needCreateExternal' and createRevert:
                        try:
                            item = self.env[key.odooModelName].search([('id','=',key.odooId)])
                            if item:
                                sfAttributes = translator.translateToSF(item, self)
                                sfInstance = externalInstance.getConnection()
                                sfRecord = getattr(sfInstance, extModelName).create(sfAttributes)
                                print('Create new record in Salesforce: {}'.format(item.name))
                                _logger.info('Create new record in Salesforce: {}'.format(item.name))
                                key.externalId = sfRecord['id']
                                key.state ='upToDate'
                                i += 1
                                print(str(i)+' / '+str(nbMaxRecords))
                                _logger.info(str(i)+' / '+str(nbMaxRecords))
                        except SalesforceMalformedRequest as error: 
                            print('Error : '+ item.name)
                            print(error.url)
                            print(error.content)
                            _logger.error(error.content)