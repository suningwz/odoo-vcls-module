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

from odoo import models, fields, api

class SFAccountSync(models.Model):
    _name = 'etl.salesforce.account'
    _inherit = 'etl.sync.mixin'

    def run(self, isFullUpdate, createInOdoo, updateInOdoo, createRevert, updateRevert, nbMaxRecords):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        translator = TranslatorSFAccount.TranslatorSFAccount(sfInstance.getConnection())
        SF = self.env['etl.salesforce.account'].search([])
        if not SF:
            SF = self.env['etl.salesforce.account'].create({})

        ##### CODE HERE #####
        SF.updateKeyTable(sfInstance, isFullUpdate)
        print('Updated key table done')
        if createInOdoo or updateInOdoo:
            SF.updateOdooInstance(translator,sfInstance, createInOdoo, updateInOdoo, nbMaxRecords)
        print('Updated odoo instance done')
        if createRevert or updateRevert:
            SF.updateExternalInstance(translator,sfInstance, createRevert, updateRevert, nbMaxRecords)
        print('Updated sf instance done')
        ##### CODE HERE #####
        SF.setNextRun()

    def updateKeyTable(self, externalInstance, isFullUpdate):
        # put logger here
        sql = 'SELECT Id, LastModifiedDate FROM Account WHERE ((Supplier__c = True or Is_supplier__c = True) or (Project_Controller__c != null and VCLS_Alt_Name__c != null))'
        if not isFullUpdate:
            sql += ' AND LastModifiedDate > ' + self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") 
        sql += ' ORDER BY Name'
        print('Execute QUERY: {}'.format(sql))
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records'] # Get modified records in External Instance
        modifiedRecordsOdoo = self.env['res.partner'].search([('write_date','>', self.getStrLastRun()),('is_company','=',True)])
        

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
        sql = 'SELECT Id, Name, Supplier_Category__c, '
        sql += 'Supplier_Status__c, Account_Level__c, LastModifiedDate, '
        sql += 'BillingCountry, BillingState, BillingAddress, BillingStreet, '
        sql += 'Phone, Fax, Area_of_expertise__c, Sharepoint_Folder__c, '
        sql += 'Supplier_Description__c, Key_Information__c, Project_Assistant__c, '
        sql += 'Supplier_Selection_Form_completed__c, Website, '
        sql += 'Create_Sharepoint_Folder__c, OwnerId, Is_supplier__c, Main_VCLS_Contact__c, '
        sql += 'Supplier__c, Type, Project_Controller__c, VCLS_Alt_Name__c,  '
        sql += 'Supplier_Project__c, Activity__c, Product_Type__c, Industry, CurrencyIsoCode, Invoice_Administrator__c '
        sql += 'FROM Account '
        sql += 'WHERE ((Supplier__c = True or Is_supplier__c = True) or (Project_Controller__c != null and VCLS_Alt_Name__c != null)) '
        
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
                            record.image=record._get_default_image(False, odooAttributes.get('is_company'), False)
                            record.write(odooAttributes)
                            print('Updated record in Odoo: {}'.format(item['Name']))
                            key.state ='upToDate'
                            i += 1
                            print(str(i)+' / '+str(nbMaxRecords))
                        except ValueError as error:
                            print("Error when writing in Odoo")
                            _logger.error("Error when writing in Odoo")
                            print(error)
                            _logger.error(error)


                elif key.state == 'needCreateOdoo' and createInOdoo:
                    for record in Modifiedrecords:
                        if record['Id'] == key.externalId:
                            item = record
                    if item:
                        try:
                            odooAttributes = translator.translateToOdoo(item, self, externalInstance)
                            partner_id = self.env['res.partner'].create(odooAttributes).id
                            print('Create new record in Odoo: {}'.format(item['Name']))
                            key.odooId = partner_id
                            key.state ='upToDate'
                            i += 1
                            print(str(i)+' / '+str(nbMaxRecords))
                        except ValueError as error:
                            print("Error when creating in Odoo")
                            _logger.error("Error when creating in Odoo")
                            print(error)
                            _logger.error(error)
    
    def updateExternalInstance(self, translator, externalInstance, createRevert, updateRevert, nbMaxRecords):
        if not nbMaxRecords:
            nbMaxRecords = len(self.keys)
        i = 0
        for key in self.keys:
            item = None
            if i < nbMaxRecords:
                if key.state == 'needUpdateExternal' and updateRevert:
                    item = self.env['res.partner'].search([('id','=',key.odooId)])
                    sfAttributes = translator.translateToSF(item, self)
                    _logger.debug(sfAttributes)
                    sfRecord = externalInstance.getConnection().Account.update(key.externalId,sfAttributes)
                    print('Update record in Salesforce: {}'.format(item.name))
                    _logger.debug('Update record in Salesforce: {}'.format(item.name))
                    key.state ='upToDate'
                    i += 1
                elif key.state == 'needCreateExternal' and createRevert:
                    try:
                        item = self.env['res.partner'].search([('id','=',key.odooId)])
                        if item:
                            sfAttributes = translator.translateToSF(item, self)
                            _logger.debug(sfAttributes)
                            _logger.debug("This dictionnary will be create in Account")
                            sfRecord = externalInstance.getConnection().Account.create(sfAttributes)
                            print('Create new record in Salesforce: {}'.format(item.name))
                            _logger.debug("This dictionnary will be create in Account")
                            key.externalId = sfRecord['id']
                            key.state ='upToDate'
                            i += 1
                            print(str(i)+' / '+str(nbMaxRecords))
                    except SalesforceMalformedRequest: 
                        print('Duplicate : '+ item.name)


