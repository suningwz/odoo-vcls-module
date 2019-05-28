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
        return self.env['res.partner'].search([('write_date','>', self.getStrLastRun()),('is_company','=',False)])

    def getKeysFromOdoo(self):                
        return self.env['etl.sync.keys'].search([('odooModelName','=','res.partner'),('externalObjName','=','Contact')])
    
    def createKey(self, odooId, externalId):
        values = {'odooModelName':'res.partner','externalObjName':'Contact'}
        if odooId:
            values.update({'odooId': odooId})
        elif externalId:
            values.update({'externalId':externalId})
        self.env['etl.sync.keys'].create(values)
    def run(self, isFullUpdate, createInOdoo, updateInOdoo, createRevert, updateRevert, nbMaxRecords):
        # run the ETL
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        translator = TranslatorSFContact.TranslatorSFContact(sfInstance.getConnection())
        SF = self.env['etl.salesforce.contact'].search([], limit = 1)
        if not SF:
            SF = self.env['etl.salesforce.contact'].create({})


        isFinished = SF.updateKeyTable(sfInstance, isFullUpdate)
        
        if isFullUpdate:
            cronId = self.env.ref('vcls-etl.cron_etl_contact_full_Update').id
        else:
            cronId = self.env.ref('vcls-etl.cron_etl_contact').id

        if isFinished :
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
            
            SF.setNextRun()
            
            relauncher = self.env.ref('vcls-etl.etl_relauncher')
            relauncher.write({'active': False,'nextcall': datetime.now()})
            self.env.ref('vcls-etl.ETL_ToRelaunch').write({'value':'ETL'})
            
        else:
            relauncher = self.env.ref('vcls-etl.etl_relauncher')
            relauncher.write({'active':True, 'nextcall': (datetime.now() + timedelta(seconds=15))})
            self.env.ref('vcls-etl.ETL_ToRelaunch').write({'value': cronId})

    def updateKeyTable(self, externalInstance, isFullUpdate):
        sql =  'SELECT C.Id, C.LastModifiedDate '
        sql += 'FROM Contact as C '
        sql += 'Where C.AccountId In ('
        sql +=  'SELECT A.Id '
        sql +=  'FROM Account as A '
        sql +=  'WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)'
        sql += ') '
        if not isFullUpdate:
            sql += ' AND LastModifiedDate > ' + self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") 
        sql += ' ORDER BY Name'
        print('Execute QUERY: {}'.format(sql))
        _logger.info('Execute QUERY: {}'.format(sql))
        
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']
        modifiedRecordsOdoo = self.env['res.partner'].search([('write_date','>', self.getStrLastRun()),('is_company','=',False)])
        
        j = 0
        i = 0

        for extRecord in modifiedRecordsExt:
            if i < 200:
                try:
                    lastModifiedExternal = datetime.strptime(extRecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")
                    lastModifiedOdoo = self.getLastUpdate(self.toOdooId(extRecord['Id']))
                    
                    if isFullUpdate or not self.isDateOdooAfterExternal(lastModifiedOdoo, lastModifiedExternal):
                        # Exist in Odoo & External
                        # External is more recent
                        keyFromExt = self.getKeyFromExtId(extRecord['Id'])[0]
                        if keyFromExt.odooId:
                            keyFromExt.setState('needUpdateOdoo')
                            print('Update Key Table needUpdateOdoo, ExternalId :{}'.format(extRecord['Id']))
                            _logger.info('Update Key Table needUpdateOdoo, ExternalId :{}'.format(extRecord['Id']))
                        else:
                            #if keyFromExt.state != 'needCreateOdoo'
                            keyFromExt.setState('needCreateOdoo')
                            print('Update Key Table needCreateOdoo, ExternalId :{}'.format(extRecord['Id']))
                            _logger.info('Update Key Table needCreateOdoo, ExternalId :{}'.format(extRecord['Id']))
                    else:
                        # Exist in Odoo & External
                        # Odoo is more recent
                        keyFromExt = self.getKeyFromExtId(extRecord['Id'])[0]
                        if keyFromExt.externalId:
                            keyFromExt.setState('needUpdateExternal')
                            print('Update Key Table needUpdateExternal, ExternalId :{}'.format(extRecord['Id']))
                            _logger.info('Update Key Table needUpdateExternal, ExternalId :{}'.format(extRecord['Id']))
                        else:
                            keyFromExt.setState('needCreateExternal')
                            print('Update Key Table needCreateExternal, ExternalId :{}'.format(keyFromExt.externalId))
                            _logger.info('Update Key Table needCreateExternal, ExternalId :{}'.format(keyFromExt.externalId))
                except (generalSync.KeyNotFoundError, ValueError):
                    # Exist in External but not in Odoo
                    self.addKeys(externalId = extRecord['Id'], odooId = None, state = 'needCreateOdoo')
                    print('Update Key Table needCreateOdoo, ExternalId :{}'.format(extRecord['Id']))
                    _logger.info('Update Key Table needCreateOdoo, ExternalId :{}'.format(extRecord['Id']))
                    i += 1
                    print(str(i)+' / 200')
                    _logger.info(str(i)+' / 200')
                j += 1
            else:
                break
        for odooRecord in modifiedRecordsOdoo:
            if i < 200:
                try:
                    key = self.getKeyFromOdooId(str(odooRecord.id))[0]
                    # Exist in Odoo & External
                    # Odoo is more recent
                    if key.state == 'upToDate':
                        key.setState('needUpdateExternal')
                        print('Update Key Table needUpdateExternal, OdooId :{}'.format(str(odooRecord.id)))
                        _logger.info('Update Key Table needUpdateExternal, ExternalId :{}'.format(extRecord['Id']))
                except (generalSync.KeyNotFoundError, ValueError):
                    # Exist in Odoo but not in External
                    self.addKeys(externalId = None, odooId = str(odooRecord.id), state = 'needCreateExternal')
                    print('Update Key Table needCreateExternal, OdooId :{}'.format(str(odooRecord.id)))
                    _logger.info('Update Key Table needCreateExternal, OdooId :{}'.format(str(odooRecord.id)))
                    i += 1
                    print(str(i)+' / 200')
                    _logger.info(str(i)+' / 200')
                j += 1
            else:
                break

        print(str(j)+' / '+str(len(modifiedRecordsExt) + len(modifiedRecordsOdoo)) )
        _logger.info(str(j)+' / '+str(len(modifiedRecordsExt) + len(modifiedRecordsOdoo)) )
        if j == (len(modifiedRecordsExt) + len(modifiedRecordsOdoo)):
            return True
        return False
            


    def updateOdooInstance(self, translator,externalInstance, createInOdoo, updateInOdoo, nbMaxRecords):
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
        
        Modifiedrecords = externalInstance.getConnection().query_all(sql + ' ORDER BY Name')['records'] #All records
        if not nbMaxRecords:
            nbMaxRecords = len(self.keys)
        i = 0
        for key in self.keys:
            item = None
            if i < nbMaxRecords:
                if key.state == 'needUpdateOdoo' and updateInOdoo:
                    for record in Modifiedrecords:
                        if record['Id'] == key.externalId:
                            item = record
                    if item:
                        try:
                            odooAttributes = translator.translateToOdoo(item, self, externalInstance)
                            record = self.env['res.partner'].search([('id','=',key.odooId)], limit=1)
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
                        partner_id = self.env['res.partner'].create(odooAttributes).id
                        print('Create new record in Odoo: {}'.format(item['Name']))
                        _logger.info('Create new record in Odoo: {}'.format(item['Name']))
                        key.odooId = partner_id
                        key.state ='upToDate'
                        i += 1
                        print(str(i)+' / '+str(nbMaxRecords))
                        _logger.info(str(i)+' / '+str(nbMaxRecords))
                
               

    def updateExternalInstance(self, translator, externalInstance, createRevert, updateRevert, nbMaxRecords):
        keysTable = self.keys
        if not nbMaxRecords:
            nbMaxRecords = len(keysTable)
        i = 0
        for key in keysTable:
            item = None
            if i < nbMaxRecords:
                if key.state == 'needUpdateExternal' and updateRevert:
                    try:   
                        item = self.env['res.partner'].search([('id','=',key.odooId)])
                        if item:
                            sfAttributes = translator.translateToSF(item, self)
                            sfRecord = externalInstance.getConnection().Contact.update(key.externalId,sfAttributes)
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
                        item = self.env['res.partner'].search([('id','=',key.odooId)])
                        if item:
                            sfAttributes = translator.translateToSF(item, self)
                            _logger.debug(sfAttributes)
                            sfRecord = externalInstance.getConnection().Contact.create(sfAttributes)
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