# -*- coding: utf-8 -*-

from odoo import models, fields, api

import datetime, pytz

from abc import ABC,abstractmethod

from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
from . import ETL_SF

class KeyNotFoundError(Exception):
    pass

class ETLMap(models.Model):
    _name = 'etl.sync.keys'
    _description = 'Mapping table to link Odoo ID with external ID'

    odooId = fields.Char(readonly = True)
    externalId = fields.Char(readonly = True)
    odooModelName = fields.Char(readonly = True)
    externalObjName = fields.Char(readonly = True)
    lastModifiedExternal = fields.Datetime(readonly = True)
    lastModifiedOdoo = fields.Datetime(readonly = True)
    
    state = fields.Selection([
        ('upToDate', 'Up To Date'),
        ('needUpdateOdoo', 'Need Update In Odoo'),
        ('needUpdateExternal', 'Need Update In External'),
        ('needCreateOdoo', 'Need To Be Created In Odoo'),
        ('needCreateExternal', 'Need To Be Created In External')],
        string='State',
        default='upToDate' # For existing keys
    )

    @api.one
    def setState(self, state):
        self.state = state
    
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

class GeneralSync(models.AbstractModel):
    _name = 'etl.sync.mixin'
    _description = 'This model represents an abstract parent class used to manage ETL'
    
    lastRun = fields.Datetime(readonly = True)

    def setNextRun(self):
        self.lastRun = fields.Datetime.from_string(datetime.datetime.now(pytz.timezone("GMT")).strftime("%Y-%m-%d %H:%M:%S.00+0000"))
        print(self.lastRun)
    
    def getStrLastRun(self):
        if not self.lastRun:
            return fields.Datetime.from_string('2000-01-01 00:00:00.000000+00:0')
        return self.lastRun
    
    @api.model
    def getLastUpdate(self, OD_id):
        partner = self.env['res.partner']
        odid = int(OD_id[0])
        record = partner.browse([odid])
        return str(record.write_date)

    @staticmethod
    def isDateOdooAfterExternal(dateOdoo,dateExternal):
        return dateOdoo >= dateExternal

    """ abstractmethods that need not be implemented in inherited Models
    def updateKeyTables(self):
    def updateOdooInstance(self):
    def needUpdateExternal(self):
    def updateKeyTable(self, externalInstance): """



