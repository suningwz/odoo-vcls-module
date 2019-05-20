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

    def getFromExternal(self, translator, externalInstance, fullUpdate,updateKeyTables, createInOdoo, updateInOdoo):
        nbMaxRecords = None
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
        launchMod = 'Get From External : \n' # func
        if nbMaxRecords:
            launchMod += '-Max records : '+ str(nbMaxRecords)
        if updateKeyTables:
            launchMod += '-Update Key Tables \n'
        if fullUpdate:
            launchMod += '-FullUpdate \n'
        if createInOdoo:
            launchMod += '-Create In Odoo \n'
        if updateInOdoo:
            launchMod += '-Update In Odoo \n'
        print(launchMod)
        
        if updateKeyTables: # to change
            modifiedRecordsSF = externalInstance.query(sql + ' ORDER BY Name')['records']
            modifiedRecordsOD = self.env['res.partner'].search([('is_company','=',True)])
            self.updateKeys(modifiedRecordsSF, modifiedRecordsOD)
        if fullUpdate:
            Modifiedrecords = externalInstance.query(sql + ' ORDER BY Name')['records']
        else:
            Modifiedrecords = externalInstance.query(sql +' AND LastModifiedDate > '+ self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000")+ ' ORDER BY Name')['records']
        if nbMaxRecords != None:
            i = 0
            for SFrecord in Modifiedrecords:
                if i < nbMaxRecords:
                    try:
                        if fullUpdate or not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOdooId(SFrecord['Id'])), datetime.strptime(SFrecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")):
                            if updateInOdoo:
                                if self.update(SFrecord, translator, externalInstance):
                                    i += 1
                    except (generalSync.KeyNotFoundError, ValueError):
                        if createInOdoo:
                            self.createRecord(SFrecord, translator, externalInstance)
                            i += 1
                    
        else: 
            for SFrecord in Modifiedrecords:
                try:
                    if fullUpdate or not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOdooId(SFrecord['Id'])), datetime.strptime(SFrecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")):
                        if updateInOdoo:
                            self.update(SFrecord, translator, externalInstance)
                except (generalSync.KeyNotFoundError, ValueError):
                    if createInOdoo:
                        self.createRecord(SFrecord, translator, externalInstance)

    def updateKeys(self, recordsSf, recordsOd):
        print("Update Keys")
        self.initExistField()
        for SFrecord in recordsSf:
            try:
                self.toOdooId(SFrecord['Id'])
                self.externalExist(SFrecord['Id'])
            except generalSync.KeyNotFoundError:
                ("Does not exist in odoo")
        for recordOd in recordsOd:
            try:
                self.toExternalId(str(recordOd.id))
                self.odooExist(str(recordOd.id))
            except generalSync.KeyNotFoundError:
                ("Does not exist in SalesForce")
        self.deleteKeys()

    def setToExternal(self, translator, externalInstance, time, createRevert, updateRevert):
        launchMod = 'Get From External : \n'
        if createRevert:
            launchMod += '-Create Revert'
        if updateRevert:
            launchMod += '-Update Revert'
        print(launchMod)
        time1 = self.getStrLastRun()
        print(time1)
        time = time.replace(second = time.second - 1)
        print('{} < record < {}'.format(time1, time))
        modifiedRecords = self.env['res.partner'].search([('write_date','>',time1),('write_date','<',time),('is_company','=',True)])
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
        if not self.getisUpdate(item['Id'])[0]:
            odooAttributes = translator.translateToOdoo(item, self, externalInstance)
            partner = self.env['res.partner']
            odid = int(OD_id[0])
            record = partner.browse([odid])
            record.image=record._get_default_image(False, odooAttributes.get('is_company'), False)
            record.write(odooAttributes)
            self.updateKey(item['Id'])
            print('Updated record in Odoo: {}'.format(item['Name']))
            if self.allIsUpdated()[0]:
                self.allNotIsUpdate()
                print('all')
            return True
        if self.allIsUpdated()[0]:
                self.allNotIsUpdate()
                print('all')
        return False

    def createRecord(self, item, translator,externalInstance):
        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
        partner_id = self.env['res.partner'].create(odooAttributes).id
        print('Create new record in Odoo: {}'.format(item['Name']))
        self.addKeys(item['Id'], partner_id)
        self.updateKey(item['Id'])
        if self.allIsUpdated()[0]:
            self.allNotIsUpdate()
            print('all')

    def createSF(self,item,translator,externalInstance):
        try:
            sfAttributes = translator.translateToSF(item, self)
            _logger.debug(sfAttributes)
            _logger.debug("This dictionnary will be create in Account")
            sfRecord = externalInstance.Account.create(sfAttributes)
            print('Create new record in Salesforce: {}'.format(item.name))
            self.addKeys(sfRecord['id'], item.id)
        except SalesforceMalformedRequest: 
            print('Malformed Query'+ item.name)
