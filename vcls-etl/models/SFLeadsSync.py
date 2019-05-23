from . import TranslatorSFLeads
from . import ETL_SF
from . import generalSync

import pytz
from simple_salesforce import Salesforce
from tzlocal import get_localzone
from datetime import datetime

from odoo import models, fields, api

class SFLeadsSync(models.Model):
    _name = 'etl.salesforce.leads'
    _inherit = 'etl.sync.mixin'

    def run(self,isFullUpdate, createInOdoo, updateInOdoo):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        print('Connecting to the Saleforce Database')
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        translator = TranslatorSFLeads.TranslatorSFLeads(sfInstance.getConnection())
        SF = self.env['etl.salesforce.leads'].search([])
        if not SF:
            SF = self.env['etl.salesforce.leads'].create({})
        SF[0].getFromExternal(translator, sfInstance.getConnection(),isFullUpdate, createInOdoo, updateInOdoo)
        SF[0].setNextRun()

    def getFromExternal(self, translator, externalInstance, fullUpdate, createInOdoo, updateInOdoo):
        
        sql = 'Select Id, Name, OwnerId, Activity__c, Address, City, Company, Content_Name__c, Country,PostalCode, Street, '
        sql += 'CurrencyIsoCode, Email,First_VCLS_Contact_Point__c, '
        sql += 'External_Referee__c, Fax, Functional_Focus__c, Inactive_Lead__c, Industry, Contact_us_Message__c, Initial_Product_Interest__c, '
        sql += 'LastModifiedDate, Title, Seniority__c, Phone, Website, Description, LeadSource From Lead'
        
        if fullUpdate:
            Modifiedrecords = externalInstance.query_all(sql + ' ORDER BY O.Name')['records']
        else:
            Modifiedrecords = externalInstance.query_all(sql +' And O.LastModifiedDate > '+ self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") + ' ORDER BY O.Name')['records']
        
        for SFrecord in Modifiedrecords:
            try:
                if fullUpdate or not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOdooId(SFrecord['Id'])), datetime.strptime(SFrecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")):
                    if updateInOdoo:
                        self.update(SFrecord, translator, externalInstance)
            except (generalSync.KeyNotFoundError, ValueError):
                if createInOdoo:
                    self.createRecord(SFrecord, translator, externalInstance)
                

    def update(self, item, translator,externalInstance):
        OD_id = self.toOdooId(item['Id'])
        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
        opportunity = self.env['crm.lead']
        odid = int(OD_id[0])
        record = opportunity.browse([odid])
        record.write(odooAttributes)
        print('Updated record in Odoo: {}'.format(item['Name']))

    def createRecord(self, item, translator,externalInstance):
        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
        opportunity_id = self.env['crm.lead'].create(odooAttributes).id
        print('Create new record in Odoo: {}'.format(item['Name']))
        self.addKeys(item['Id'], opportunity_id)

    def updateKeyTable(self, externalInstance, isFullUpdate):
        sql =  'SELECT C.Id, C.LastModifiedDate '
        sql += 'FROM Lead'
        
        if not isFullUpdate:
            sql += ' AND LastModifiedDate > ' + self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") 
        sql += ' ORDER BY Name'
        print('Execute QUERY: {}'.format(sql))
        _logger.info('Execute QUERY: {}'.format(sql))
        
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']
        modifiedRecordsOdoo = self.env['res.partner'].search([('write_date','>', self.getStrLastRun()),('is_company','=',False)])

        for extRecord in modifiedRecordsExt:
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
                    else:
                        keyFromExt.setState('needCreateOdoo')
                        print('Update Key Table needCreateOdoo, ExternalId :{}'.format(extRecord['Id']))
                    
                else:
                    # Exist in Odoo & External
                    # Odoo is more recent
                    keyFromExt = self.getKeyFromExtId(extRecord['Id'])[0]
                    if keyFromExt.externalId:
                        keyFromExt.setState('needUpdateExternal')
                        print('Update Key Table needUpdateExternal, ExternalId :{}'.format(extRecord['Id']))
                    else:
                        keyFromExt.setState('needCreateExternal')
                        print('Update Key Table needCreateExternal, ExternalId :{}'.format(keyFromExt.externalId))
            except (generalSync.KeyNotFoundError, ValueError):
                # Exist in External but not in Odoo
                self.addKeys(externalId = extRecord['Id'], odooId = None, state = 'needCreateOdoo')
                print('Update Key Table needCreateOdoo, ExternalId :{}'.format(extRecord['Id']))
        
        for odooRecord in modifiedRecordsOdoo:
            try:
                key = self.getKeyFromOdooId(str(odooRecord.id))[0]
                # Exist in Odoo & External
                # Odoo is more recent
                if key.state == 'upToDate':
                    key.setState('needUpdateExternal')
                    print('Update Key Table needUpdateExternal, OdooId :{}'.format(str(odooRecord.id)))
            except (generalSync.KeyNotFoundError, ValueError):
                # Exist in Odoo but not in External
                self.addKeys(externalId = None, odooId = str(odooRecord.id), state = 'needCreateExternal')
                print('Update Key Table needCreateExternal, OdooId :{}'.format(str(odooRecord.id)))


    def updateOdooInstance(self, translator,externalInstance, createInOdoo, updateInOdoo, nbMaxRecords):
        sql = 'Select Id, Name, OwnerId, Activity__c, Address, City, Company, Content_Name__c, Country,PostalCode, Street, '
        sql += 'CurrencyIsoCode, Email,First_VCLS_Contact_Point__c, '
        sql += 'External_Referee__c, Fax, Functional_Focus__c, Inactive_Lead__c, Industry, Contact_us_Message__c, Initial_Product_Interest__c, '
        sql += 'LastModifiedDate, Title, Seniority__c, Phone, Website, Description, LeadSource From Lead'
        
        
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