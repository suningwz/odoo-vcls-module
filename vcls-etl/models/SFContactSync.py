from . import TranslatorSFContact
from . import ETL_SF
from . import generalSync
import logging
_logger = logging.getLogger(__name__)

import pytz
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
from tzlocal import get_localzone
from datetime import datetime

from odoo import models, fields, api

class SFContactSync(models.Model):
    _name = 'etl.salesforce.contact'
    _inherit = 'etl.sync.mixin'

    def run(self,isFullUpdate, updateKeyTables, createInOdoo, updateInOdoo, createRevert, updateRevert):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        
        time = datetime.now(pytz.timezone("GMT"))
        print('Connecting to the Saleforce Database')
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        translator = TranslatorSFContact.TranslatorSFContact(sfInstance.getConnection())
        SF = self.env['etl.salesforce.contact'].search([])
        if not SF:
            SF = self.env['etl.salesforce.contact'].create({})
        SF[0].getFromExternal(translator, sfInstance.getConnection(),isFullUpdate, createInOdoo, updateInOdoo)
        #SF[0].setToExternal(translator, sfInstance.getConnection(), time, createRevert, updateRevert)
        SF[0].setNextRun()
        #


    def getFromExternal(self, translator, externalInstance, fullUpdate, createInOdoo, updateInOdoo):
        
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
        
        if fullUpdate:
            Modifiedrecords = externalInstance.query(sql+' ORDER BY C.Name')['records']
        else:
            Modifiedrecords = externalInstance.query(sql +' And C.LastModifiedDate > '+ self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000")+' ORDER BY C.Name')['records']
        
        for SFrecord in Modifiedrecords:
            try:
                if fullUpdate or not self.isDateOdooAfterExternal(self.getLastUpdate(self.toOdooId(SFrecord['Id'])), datetime.strptime(SFrecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")):
                    if updateInOdoo:
                        self.update(SFrecord, translator, externalInstance)
            except (generalSync.KeyNotFoundError, ValueError):
                if createInOdoo:
                    self.createRecord(SFrecord, translator, externalInstance)
        #here


    def setToExternal(self, translator, externalInstance, time, createRevert, updateRevert):
        time1 = self.getStrLastRun()
        print(time1)
        if time.second >=1:
            time = time.replace(second = time.second - 1)
        else:
            time = time.replace(second = 59)
        print(time)
        modifiedRecords = self.env['res.partner'].search([('write_date','>',time1),('write_date','<',time),('is_company','=',False)])
        print(modifiedRecords)
        for record in modifiedRecords:
            try:
                self.toExternalId(str(record.id))
                if updateRevert:
                    self.updateSF(record,translator,externalInstance)
            except (generalSync. KeyNotFoundError, ValueError):
                if createRevert:
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
    
    def createSF(self,item,translator,externalInstance):
        try:
            sfAttributes = translator.translateToSF(item, self)
            _logger.debug(sfAttributes)
            _logger.debug("This dictionnary will be create in Account")
            sfRecord = externalInstance.Contact.create(sfAttributes)
            print('Create new record in Salesforce: {}'.format(item.name))
            self.addKeys(sfRecord['id'], item.id)
        except SalesforceMalformedRequest: 
            print('Duplicate : '+ item.name)

