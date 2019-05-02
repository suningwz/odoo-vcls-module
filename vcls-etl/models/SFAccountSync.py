
from odoo import models, fields, api

from pythonClass import TranslatorSF, ETL_SF
from datetime import datetime
from generalSync import KeyNotFoundError

class SFAccountSync(models.Model):
    _name = 'etl.salesforce.account'
    _inherit = 'etl.sync.mixin'

    def run(self):
        self.translator = TranslatorSF()
        self.sfInstance = ETL_SF.getInstance()
        self.getFromExternal(self.translator,self.sfInstance)
        ##self.setToExternal(TranslatorSF(),ETL_SF.getInstance())
        self.setNextRun()


    def getFromExternal(self, translator, externalInstance):
        sql = 'SELECT Id, Name, Supplier_Category__c, Supplier_Status__c, Account_Level__c, LastModifiedDate, BillingCountry, BillingState, BillingAddress, BillingStreet, Phone, Fax, Area_of_expertise__c, Sharepoint_Folder__c, Supplier_Description__c, Key_Information__c, Supplier_Selection_Form_completed__c, Website, Create_Sharepoint_Folder__c, OwnerId, Is_supplier__c, Type FROM Account WHERE (Supplier__c = True or Is_supplier__c = True) AND LastModifiedDate > '
        Modifiedrecords = externalInstance.query(sql)
        for SFrecord in Modifiedrecords:
            try:
                if not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOD_id(SFrecord['Id'])), SFrecord['LastModifiedDate']):
                    self.update(SFrecord)
            except (KeyNotFoundError, ValueError) as error:
                self.create(SFrecord)

    def setToExternal(self, translator, externalInstance):
        pass

    def update(self, item):
        OD_id = self.toOD_id(item['Id'])
        odooAttributes = self.translator.translateToOdoo(item)   
        self.partner.write([OD_id], odooAttributes)
        print('Updated record in Odoo: {}'.format(item['Name']))

    def create(self, item):
        odooAttributes = self.translator.translateToOdoo(item)
        
        partner_id = self.partner.create(odooAttributes)
        print('Create new record in Odoo: {}'.format(item['Name']))
        self.addKeys(item['Id'], partner_id)