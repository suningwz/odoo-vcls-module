from odoo import models, fields, api

from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
from . import ETL_SF

class ETLMap(models.Model):
    _name = 'etl.update.keys'

    def run(self):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        self.updateAccountKey(sfInstance)
        self.updateContactKey(sfInstance)
        self.updateOpportunityKey(sfInstance)
        
    def updateAccountKey(self, externalInstance):
        sql = 'Select Id From Account WHERE ((Supplier__c = True or Is_supplier__c = True) or (Project_Controller__c != null and VCLS_Alt_Name__c != null))'
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']

        for item in modifiedRecordsExt:
            odooAccount = self.env['etl.sync.keys'].search([('externalId','=',item['Id'])], limit=1)
            if odooAccount:
                odooAccount.write({'odooModelName':'res.partner','externalObjName':'Account'})
                print("Update Key Account externalId :{}".format(item['Id']))

    def updateContactKey(self, externalInstance):
        sql =  'SELECT C.Id, C.LastModifiedDate '
        sql += 'FROM Contact as C '
        sql += 'Where C.AccountId In ('
        sql +=  'SELECT A.Id '
        sql +=  'FROM Account as A '
        sql +=  'WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)'
        sql += ') '
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']

        for item in modifiedRecordsExt:
            odooContact = self.env['etl.sync.keys'].search([('externalId','=',item['Id'])], limit=1)
            if odooContact:
                odooContact.write({'odooModelName':'res.partner','externalObjName':'Contact'})
                print("Update Key Account externalId :{}".format(item['Id']))

    def updateOpportunityKey(self, externalInstance):
        sql =  'SELECT O.Id, O.LastModifiedDate '
        sql += 'FROM Opportunity as O '
        sql += 'Where O.AccountId In ('
        sql +=  'SELECT A.Id '
        sql +=  'FROM Account as A '
        sql +=  'WHERE (A.Supplier__c = True Or A.Is_supplier__c = True) or (A.Project_Controller__c != Null And A.VCLS_Alt_Name__c != null)'
        sql += ') '
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']

        for item in modifiedRecordsExt:
            odooOpportunity = self.env['etl.sync.keys'].search([('externalId','=',item['Id'])], limit=1)
            if odooOpportunity:
                odooOpportunity.write({'odooModelName':'crm.lead','externalObjName':'Opportunity'})
