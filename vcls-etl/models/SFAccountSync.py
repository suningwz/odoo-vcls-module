from . import TranslatorSF
from . import ETL_SF
from . import generalSync
from odoo import models, fields, api
from datetime import datetime

class SFAccountSync(models.Model):
    _name = 'etl.salesforce.account'
    _inherit = 'etl.sync.mixin'

    def run(self):
        translator = TranslatorSF.TranslatorSF()
        print('Connecting to the Saleforce Database')
        sfInstance = ETL_SF.ETL_SF.getInstance()
        self.getFromExternal(translator, sfInstance.getConnection())
        ##self.setToExternal(TranslatorSF(),ETL_SF.getInstance())
        self.setNextRun()


    def getFromExternal(self, translator, externalInstance):
        sql = 'SELECT Id, Name, Supplier_Category__c, Supplier_Status__c, Account_Level__c, LastModifiedDate, BillingCountry, BillingState, BillingAddress, BillingStreet, Phone, Fax, Area_of_expertise__c, Sharepoint_Folder__c, Supplier_Description__c, Key_Information__c, Supplier_Selection_Form_completed__c, Website, Create_Sharepoint_Folder__c, OwnerId, Is_supplier__c, Type FROM Account WHERE (Supplier__c = True or Is_supplier__c = True) AND LastModifiedDate > '
        Modifiedrecords = externalInstance.query(sql + self.getStrLastRun())['records']
        print(Modifiedrecords)
        for SFrecord in Modifiedrecords:
            try:
                if not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOdooId(SFrecord['Id'])), SFrecord['LastModifiedDate']):
                    self.update(SFrecord,translator,externalInstance)
            except (generalSync.KeyNotFoundError, ValueError) as error:
                self.createRecord(SFrecord, translator,externalInstance)

    def setToExternal(self, translator, externalInstance):
        pass

    def update(self, item, translator,externalInstance):
        OD_id = self.toOdooId(item['Id'])
        odooAttributes = translator.translateToOdoo(item, self, externalInstance)   
        self.env['res.partner'].write([OD_id], odooAttributes)
        print('Updated record in Odoo: {}'.format(item['Name']))

    def createRecord(self, item, translator,externalInstance):
        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
        
        partner_id = self.env['res.partner'].create(odooAttributes).id

        print('Create new record in Odoo: {}'.format(item['Name']))
        self.addKeys(item['Id'], partner_id)
        i = self.env['etl.sync.keys'].search([('odooId','=',partner_id)])
        print(i)