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

    def getKeysFromOdoo(self):
        return "This return the keys from Odoo"
    
    def createKey(self,odooId,externalId):
        return "this will create a new key in etl.sync.keys"

    def run(self, isFullUpdate, createInOdoo, updateInOdoo, createRevert, updateRevert, nbMaxRecords):
        # run the ETL
        sfInstance = self.getSFInstance()
        translator = self.getSFTranslator(sfInstance)
        #cronId = self.getCronId(isFullUpdate)

        #initialised the SfSync Object
        SF = self.env[self._name].search([], limit = 1)
        if not SF:
            SF = self.env[self._name].create({})

        #boolean for batch
        SF.updateKeyTable(sfInstance, isFullUpdate)

        #if isFinished :
   
        print('Updated key table done')
        _logger.info('Updated key table done')
        
        if createInOdoo or updateInOdoo:
            SF.updateOdooInstance(translator,sfInstance, createInOdoo, updateInOdoo,nbMaxRecords)
        
        print('Updated odoo instance done')
        _logger.info('Updated odoo instance done')
        
        #if createRevert or updateRevert:
            #SF.updateExternalInstance(translator,sfInstance, createRevert, updateRevert, nbMaxRecords)
        
        print('Updated sf instance done')
        _logger.info('Updated sf instance done')

        print('ETL IS FINISHED')
        _logger.info('ETL IS FINISHED')
        
        SF.setNextRun()
            
    def updateKeyTable(self, externalInstance, isFullUpdate):
        keys = self.getKeysFromOdoo()
        idKeysExt = []
        idKeysOdoo = []
        if keys:
            for key in keys:
                idKeysExt.append(key.externalId)
                idKeysOdoo.append(key.odooId)
                if isFullUpdate:
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
        
        sql = str(self.getSQLForKeys())
        if not isFullUpdate:
            sql += ' AND LastModifiedDate > ' + self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") 
        sql += ' ORDER BY Name'
        
        print('Execute QUERY: {}'.format(sql))
        _logger.info('Execute QUERY: {}'.format(sql))
        
        #working on keys that were not created
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']
        idsListFromExt = []
        for record in modifiedRecordsExt:
            idsListFromExt.append(record['Id'])
        #this regroup keys that are present in Salesforce but were not created in Odoo yet        
        keysToCreate = list(set(idsListFromExt) - set(idKeysExt))
        
        for key in keysToCreate:
            self.createKey(None,key)
            print('Update Key Table needCreateOdoo, ExternalId :{}'.format(key))
            _logger.info('Update Key Table needCreateOdoo, ExternalId :{}'.format(key))
        
        modifiedRecordsOdoo = self.getModifiedRecordsOdoo()
        idsListFromOdoo = []
        for record in modifiedRecordsOdoo:
            idsListFromExt.append(record.id)
        #this regroup keys that are present in Odoo but were not created in Odoo yet        
        keysToCreate = list(set(idsListFromOdoo) - set(idKeysOdoo))
        
        for key in keysToCreate:
            self.createKey(key,None)
            print('Update Key Table needCreateExternal, OdooId : {}'.format(key))
            _logger.info('Update Key Table needCreateExternal, OdooId : {}'.format(key))
        
        
        """ print(str(j)+' / '+str(len(modifiedRecordsExt) + len(modifiedRecordsOdoo)) )
        _logger.info(str(j)+' / '+str(len(modifiedRecordsExt) + len(modifiedRecordsOdoo)) )
        if j == (len(modifiedRecordsExt) + len(modifiedRecordsOdoo)):
            return True
        return False """
            


    def updateOdooInstance(self, translator,externalInstance, createInOdoo, updateInOdoo, nbMaxRecords):
        sql = self.getSQLForRecord()
        sql += ' ORDER BY Name'
        Modifiedrecords = externalInstance.getConnection().query_all(sql)['records'] #All records
        keys = self.getKeysFromOdoo()
        if not nbMaxRecords:
            nbMaxRecords = len(keys)
        i = 0
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
                            record.write(odooAttributes)
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
                        partner_id = self.env[key.odooModelName].create(odooAttributes).id
                        print('Create new record in Odoo: {}'.format(item['Name']))
                        _logger.info('Create new record in Odoo: {}'.format(item['Name']))
                        key.odooId = partner_id
                        key.state ='upToDate'
                        i += 1
                        print(str(i)+' / '+str(nbMaxRecords))
                        _logger.info(str(i)+' / '+str(nbMaxRecords))
                
               

    def updateExternalInstance(self, translator, externalInstance, createRevert, updateRevert, nbMaxRecords):
        keysTable = self.getKeysFromOdoo()
        if not nbMaxRecords:
            nbMaxRecords = len(keysTable)
        i = 0
        for key in keysTable:
            item = None
            if i < nbMaxRecords:
                if key.state == 'needUpdateExternal' and updateRevert:
                    try:   
                        item = self.env[key.odooModelName].search([('id','=',key.odooId)])
                        if item:
                            sfAttributes = translator.translateToSF(item, self)
                            #sfRecord = externalInstance.getConnection().key.update(key.externalId,sfAttributes)
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
                            #sfRecord = externalInstance.getConnection().Contact.create(sfAttributes)
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