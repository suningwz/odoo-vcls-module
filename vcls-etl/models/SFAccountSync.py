from . import TranslatorSF
from . import ETL_SF
from simple_salesforce import Salesforce
from . import generalSync
from tzlocal import get_localzone
import pytz
from odoo import models, fields, api
from datetime import datetime

class SFAccountSync(models.Model):
    _name = 'etl.salesforce.account'
    _inherit = 'etl.sync.mixin'

    def run(self,isFullUpdate):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
       # time = datetime.now(pytz.timezone("GMT"))
        translator = TranslatorSF.TranslatorSF()
        print('Connecting to the Saleforce Database')
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        SF = self.env['etl.salesforce.account'].search([])
        if not SF:
            SF = self.env['etl.salesforce.account'].create({})
        SF[0].getFromExternal(translator, sfInstance.getConnection(),isFullUpdate)
       # SF[0].setToExternal(translator, sfInstance.getConnection(), time)
        SF[0].setNextRun()
        
    def getFromExternal(self, translator, externalInstance, fullUpdate):
        
        sql = 'SELECT Id, Name, Supplier_Category__c, Supplier_Status__c, Account_Level__c, LastModifiedDate, BillingCountry, BillingState, BillingAddress, BillingStreet, Phone, Fax, Area_of_expertise__c, Sharepoint_Folder__c, Supplier_Description__c, Key_Information__c, Supplier_Selection_Form_completed__c, Website, Create_Sharepoint_Folder__c, OwnerId, Is_supplier__c, Supplier__c, Type FROM Account WHERE (Supplier__c = True or Is_supplier__c = True)'
        
        if fullUpdate:
            Modifiedrecords = externalInstance.query(sql)['records']
        else:
            Modifiedrecords = externalInstance.query(sql +' AND LastModifiedDate > '+ self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000"))['records']
        
        for SFrecord in Modifiedrecords:
            try:
                if fullUpdate or not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOdooId(SFrecord['Id'])), datetime.strptime(SFrecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")):
                    self.update(SFrecord, translator, externalInstance)
            except (generalSync.KeyNotFoundError, ValueError) as error:
                self.createRecord(SFrecord, translator, externalInstance)

    def setToExternal(self, translator, externalInstance, time):
        time1 = self.getStrLastRun()
        print(time1)
        time = time.replace(second = time.second - 1)
        print('{} < record < {}'.format(time1, time))
        modifiedRecords = self.env['res.partner'].search([('write_date','>',time1),('write_date','<',time)])
        print(modifiedRecords)
        for record in modifiedRecords:
            try:
                self.updateSF(record,translator,externalInstance)
            except (generalSync. KeyNotFoundError, ValueError) as error:
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
        i = self.env['etl.sync.keys'].search([('odooId','=',partner_id)])
        print(i)

    def updateSF(self,item,translator,externalInstance):
        SF_ID = self.toExternalId(str(item.id))
        sfAttributes = translator.translateToSF(item, self)
        externalInstance.Account.update(SF_ID[0],sfAttributes)
        print('Updated record in Salesforce: {}'.format(item.name))
    
    def createSF(self,item,translator,externalInstance):
        sfAttributes = translator.translateToSF(item, self)
        try:
            sfRecord = externalInstance.Account.create(sfAttributes)
            print('Create new record in Salesforce: {}'.format(item.name))
            self.addKeys(sfRecord['id'], item.id)
        except:
            print("Duplicate " + item.name)
        