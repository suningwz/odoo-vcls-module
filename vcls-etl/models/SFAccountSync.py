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

    def run(self,isFullUpdate, updateKeyTables, createInOdoo, updateInOdoo, createRevert, updateRevert):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value

        time = datetime.now(pytz.timezone("GMT"))
        print('Connecting to the Saleforce Database')

        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        translator = TranslatorSFAccount.TranslatorSFAccount(sfInstance.getConnection())

        SF = self.env['etl.salesforce.account'].search([])
        if not SF:
            SF = self.env['etl.salesforce.account'].create({})
        
        SF[0].getFromExternal(translator, sfInstance.getConnection(),isFullUpdate, updateKeyTables,createInOdoo, updateInOdoo)
        SF[0].setToExternal(translator, sfInstance.getConnection(), time, createRevert, updateRevert)
        SF[0].setNextRun()


    def updateOdooInstance(self, translator,externalInstance, nbMaxRecords):
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
        
        Modifiedrecords = externalInstance.query(sql + ' ORDER BY Name')['records'] #All records
        keysTable = self.env['etl.salesforce.account'].keys

        if not nbMaxRecords:
            #if nbMaxRecords == None / no limit
            nbMaxRecords = len(keysTable)
        print(nbMaxRecords)
        i = 0
        for key in keysTable:
            if i < nbMaxRecords:
                if key.state == 'needUpdateOdoo':
                    for record in Modifiedrecords:
                        if record['Id'] == key.externalId:
                            item = record
                    if item:
                        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
                        record = self.env['res.partner'].browse(key.odooId)
                        record.image=record._get_default_image(False, odooAttributes.get('is_company'), False)
                        record.write(odooAttributes)
                        print('Updated record in Odoo: {}'.format(item['Name']))
                        key.state =' upToDate'
                        i += 1
                elif key.state == 'needCreateOdoo':
                    for record in Modifiedrecords:
                        if record['Id'] == key.externalId:
                            item = record
                    if item:
                        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
                        partner_id = self.env['res.partner'].create(odooAttributes).id
                        print('Create new record in Odoo: {}'.format(item['Name']))
                        key.odooId = partner_id
                        i += 1
    
    def needUpdateExternal(self, translator, externalInstance, nbMaxRecords):
        keysTable = self.env['etl.salesforce.account'].keys
        if not nbMaxRecords:
            nbMaxRecords = len(keysTable)
        print(nbMaxRecords)
        i = 0
        for key in keysTable:
            if i < nbMaxRecords:
                if key.state == 'needUpdateExternal':
                    item = self.env['res.partner'].browse(key.odooId)
                    sfAttributes = translator.translateToSF(item, self)
                    _logger.debug(sfAttributes)
                    sfRecord = externalInstance.Account.update(key.externalId,sfAttributes)
                    print('Update record in Salesforce: {}'.format(item.name))
                    _logger.debug('Update record in Salesforce: {}'.format(item.name))
                    key.state =' upToDate'
                    i += 1
                elif key.state == 'needCreateExternal':
                    try:
                        item = self.env['res.partner'].browse(key.odooId)
                        if item:
                            sfAttributes = translator.translateToSF(item, self)
                            _logger.debug(sfAttributes)
                            _logger.debug("This dictionnary will be create in Account")
                            sfRecord = externalInstance.Account.create(sfAttributes)
                            print('Create new record in Salesforce: {}'.format(item.name))
                            _logger.debug("This dictionnary will be create in Account")
                            key.externalId = sfRecord['id']
                            i += 1
                    except SalesforceMalformedRequest: 
                        print('Duplicate : '+ item.name)
            

    def getFromExternal(self, translator, externalInstance, fullUpdate,updateKeyTables, createInOdoo, updateInOdoo):
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

        if fullUpdate:
            Modifiedrecords = externalInstance.query(sql + ' ORDER BY Name')['records']
        else:
            Modifiedrecords = externalInstance.query(sql +' AND LastModifiedDate > '+ self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000")+ ' ORDER BY Name')['records']
        
        for SFrecord in Modifiedrecords:
            try:
                if fullUpdate or not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOdooId(SFrecord['Id'])), datetime.strptime(SFrecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")):
                    if updateInOdoo:
                        self.update(SFrecord, translator, externalInstance)
            except (generalSync.KeyNotFoundError, ValueError):
                if createInOdoo:
                    self.createRecord(SFrecord, translator, externalInstance)

    def setToExternal(self, translator, externalInstance, time, createRevert, updateRevert):
        time1 = self.getStrLastRun()
        print(time1)
        """ if time.second >=1:
            time = time.replace(second = time.second - 1)
        else:
            time = time.replace(second = 59) """
        print('{} < record < {}'.format(time1, time))
        modifiedRecords = self.env['res.partner'].search([('write_date','>',time1),('write_date','<',time),('is_company','=',True)])
        print(modifiedRecords)
        for record in modifiedRecords:
            try:
                self.toExternalId(str(record.id))
                if updateRevert:
                    self.updateSF(record,translator,externalInstance)
            except (generalSync.KeyNotFoundError, ValueError):
                if createRevert:
                    self.createSF(record,translator,externalInstance)


    def update(self, item, translator,externalInstance):
        OD_id = self.toOdooId(item['Id'])
        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
        partner = self.env['res.partner']
        odid = int(OD_id[0])
        record = partner.browse([odid])
        record.image=record._get_default_image(False, odooAttributes.get('is_company'), False)
        record.write(odooAttributes)
        print('Updated record in Odoo: {}'.format(item['Name']))


    def createRecord(self, item, translator,externalInstance):
        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
        partner_id = self.env['res.partner'].create(odooAttributes).id
        print('Create new record in Odoo: {}'.format(item['Name']))
        self.addKeys(item['Id'], partner_id)

    def createSF(self,item,translator,externalInstance):
        try:
            sfAttributes = translator.translateToSF(item, self)
            _logger.debug(sfAttributes)
            _logger.debug("This dictionnary will be create in Account")
            sfRecord = externalInstance.Account.create(sfAttributes)
            print('Create new record in Salesforce: {}'.format(item.name))
            self.addKeys(sfRecord['id'], item.id)
        except SalesforceMalformedRequest: 
            print('Duplicate : '+ item.name)
    
    def updateKeyTable(self, externalInstance):
        # put logger here
        sql = 'SELECT Id, LastModifiedDate FROM Account WHERE ((Supplier__c = True or Is_supplier__c = True) or (Project_Controller__c != null and VCLS_Alt_Name__c != null))'
        sql += ' AND LastModifiedDate > ' + self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") + ' ORDER BY Name'
        print('Execute QUERY: {}'.format(sql))
        modifiedRecordsExt = externalInstance.getConnection().query(sql)['records'] # Get modified records in External Instance
        modifiedRecordsOdoo = self.env['res.partner'].search([('write_date','>', self.getStrLastRun()),('is_company','=',True)])
        

        for extRecord in modifiedRecordsExt:
            try:
                lastModifiedExternal = datetime.strptime(extRecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")
                lastModifiedOdoo = self.getLastUpdate(self.toOdooId(extRecord['Id']))
                
                if self.isDateOdooAfterExternal(lastModifiedOdoo, lastModifiedExternal):
                    # Exist in Odoo & External
                    # Odoo is more recent
                    self.getKeyFromExtId(extRecord['Id']).setState('needUpdateExternal')
                else:
                    # Exist in Odoo & External
                    # External is more recent
                    self.getKeyFromExtId(extRecord['Id']).setState('needUpdateOdoo')
            except (generalSync.KeyNotFoundError, ValueError):
                # Exist in External but not in Odoo
                self.addKeys(externalId = extRecord['Id'], odooId = None, state = 'needCreateOdoo')
        
        for odooRecord in modifiedRecordsOdoo:
            try:
                key = self.getKeyFromOdooId(odooRecord.id)
                # Exist in Odoo & External
                # Odoo is more recent
                if key.state == 'upToDate':
                    key.setState('needUpdateExternal')
            except (generalSync.KeyNotFoundError, ValueError):
                # Exist in Odoo but not in External
                self.addKeys(externalId = None, odooId = odooRecord.id, state = 'needCreateExternal')


    
    # TO DELETE ONCE OK
    @api.model
    def runRunRun(self):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)

        SF = self.env['etl.salesforce.account'].search([])
        if not SF:
            SF = self.env['etl.salesforce.account'].create({})
        
        ##### CODE HERE #####

        SF.updateKeyTable(sfInstance)

        ##### CODE HERE #####

        SF[0].setNextRun()


