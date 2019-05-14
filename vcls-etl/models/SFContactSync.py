from . import TranslatorSFContact
from . import ETL_SF
from . import generalSync

import pytz
from simple_salesforce import Salesforce
from tzlocal import get_localzone
from datetime import datetime

from odoo import models, fields, api

class SFContactSync(models.Model):
    _name = 'etl.salesforce.contact'
    _inherit = 'etl.sync.mixin'

    def run(self,isFullUpdate):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        
       # time = datetime.now(pytz.timezone("GMT"))
        print('Connecting to the Saleforce Database')
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        translator = TranslatorSFContact.TranslatorSFContact(sfInstance.getConnection())
        SF = self.env['etl.salesforce.contact'].search([])
        if not SF:
            SF = self.env['etl.salesforce.contact'].create({})
        SF[0].getFromExternal(translator, sfInstance.getConnection(),isFullUpdate)
       # SF[0].setToExternal(translator, sfInstance.getConnection(), time)
        SF[0].setNextRun()

    def getFromExternal(self, translator, externalInstance, fullUpdate):
        
        sql =  'SELECT C.Id, C.Name, C.AccountId, C.Phone, C.Fax, '
        sql += 'C.OwnerId, C.LastModifiedDate, C.LinkedIn_Profile__c, '
        sql += 'C.Category__c, C.Supplier__c, Salutation, C.Email, '
        sql += 'C.Title, C.MobilePhone, C.MailingAddress, C.AccountWebsite__c, '
        sql += 'C.Description, C.MailingCountry, C.Inactive_Contact__c, C.CurrencyIsoCode '
        sql += 'FROM Contact as C '
        sql += 'Where C.AccountId In ('
        sql +=  'SELECT A.Id '
        sql +=  'FROM Account as A '
        sql +=  'WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)'
        sql += ')'
        
        if fullUpdate:
            Modifiedrecords = externalInstance.query(sql)['records']
        else:
            Modifiedrecords = externalInstance.query(sql +' And C.LastModifiedDate > '+ self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000"))['records']
        
        for SFrecord in Modifiedrecords:
            try:
                if fullUpdate or not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOdooId(SFrecord['Id'])), datetime.strptime(SFrecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")):
                    self.update(SFrecord, translator, externalInstance)
            except (generalSync.KeyNotFoundError, ValueError):
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
            except (generalSync. KeyNotFoundError, ValueError):
                self.createSF(record,translator,externalInstance)


    def update(self, item, translator,externalInstance):
        OD_id = self.toOdooId(item['Id'])
        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
        partner = self.env['res.partner']
        odid = int(OD_id[0])
        record = partner.browse([odid])
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
