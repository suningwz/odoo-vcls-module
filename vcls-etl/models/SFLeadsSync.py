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
            Modifiedrecords = externalInstance.query(sql + ' ORDER BY Name')['records']
        else:
            Modifiedrecords = externalInstance.query(sql +' And LastModifiedDate > '+ self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") + ' ORDER BY O.Name')['records']
        
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