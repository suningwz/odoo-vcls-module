# -*- coding: utf-8 -*-

from odoo import models, fields, api

import datetime, pytz
from datetime import datetime

from abc import ABC,abstractmethod

from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
from . import ETL_SF

import logging
_logger = logging.getLogger(__name__)

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
    priority = fields.Integer(default=0)
    
    state = fields.Selection([
        ('upToDate', 'Up To Date'),
        ('needUpdateOdoo', 'Need Update In Odoo'),
        ('needUpdateExternal', 'Need Update In External'),
        ('needCreateOdoo', 'Need To Be Created In Odoo'),
        ('needCreateExternal', 'Need To Be Created In External')],
        string='State',
        default='upToDate' # For existing keys
    )
    migration_running = fields.Boolean()

    @api.one
    def setState(self, state):
        self.state = state
    
    """def run(self):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        self.updateAccountKey(sfInstance)
        self.updateContactKey(sfInstance)
        self.updateOpportunityKey(sfInstance)"""
    
    def open_con(self):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        return ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
    
    def update_keys(self,params={}):
        _logger.info("ETL | UPDATE KEYS {}".format(params))
        rec_ext = params['sfInstance'].getConnection().query_all(params['sql'])['records']
        keys_exist = self.search([('externalObjName','=',params['externalObjName']),('odooModelName','=',params['odooModelName'])])
        keys_exist_sfid = keys_exist.mapped('externalId')
        keys_create = keys_exist.filtered(lambda k: k.externalId and not k.odooId)
        keys_update = keys_exist.filtered(lambda k: k.externalId and k.odooId)
        keys_ok = self.env['etl.sync.keys']

        """# Mass Status Update
        keys_exist.filtered(lambda k: k.externalId and not k.odooId).write({'state':'needCreateOdoo','priority':params['priority']})
        keys_exist.filtered(lambda k: not k.externalId and k.odooId).write({'state':'needCreateExternal','priority':params['priority']})
        if params['is_full_update']:
            keys_exist.filtered(lambda k: k.externalId and k.odooId).write({'state':'needUpdateOdoo','priority':params['priority']})
        """
        #We look for non exisitng keys
        for rec in rec_ext:
            if rec['Id'] not in keys_exist_sfid: #if the rec does not exists
                vals = {
                    'externalObjName':params['externalObjName'],
                    'externalId': rec['Id'],
                    'lastModifiedExternal': datetime.strptime(rec['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000"),
                    'odooModelName': params['odooModelName'],
                    'state':'needCreateOdoo',
                    'priority':params['priority'],
                }
                keys_create |= self.create(vals)
                _logger.info("KEYS | New creation {}".format(vals))


            elif not params['is_full_update']: #if we don't want a full update, we need to compare dates
                key = keys_update.filtered(lambda k: k.externalId==rec['Id'])
                if key:
                    if key[0].lastModifiedOdoo:
                        ext_date = datetime.strptime(rec['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000")
                        if ext_date > key[0].lastModifiedOdoo:
                            keys_update |= key
                        else:
                            keys_ok |= key
                    else:
                        keys_update |= key
                        
    
        if rec_ext:
            _logger.info("QUERY |\n{}\nreturned {} {} records".format(params['sql'],len(rec_ext),params['externalObjName']))
        if keys_exist:
            _logger.info("KEYS | Found {} existing keys".format(len(keys_exist)))

        if keys_create:
            keys_create.write({'state':'needCreateOdoo','priority':params['priority']})
            _logger.info("KEYS | {} Keys to create".format(len(keys_create)))
        if keys_update:
            keys_update.write({'state':'needUpdateOdoo','priority':params['priority']})
            _logger.info("KEYS | {} Keys to update".format(len(keys_update)))
        if keys_ok:
            keys_ok.write({'state':'upToDate','priority':params['priority']})
            _logger.info("KEYS | {} Keys are OK".format(len(keys_ok)))
        

    def accounts_and_contacts(self, is_full_update=True):
        """
        We 1st process the keys and priorities, starting from contacts.
        But then the queue must be executed in revert order of priorities to ensure parent accounts to be created 1st, etc.
        """
        ### PREPARATION
        #Update the context to execute vcls-rdd override
        self.env.user.context_data_integration = True
        #Clean the keys table of corrupted entries
        to_clean = self.search([('odooModelName','=',False)])
        for key in to_clean:
            key.unlink()
        
        #get instance
        sfInstance = self.open_con()

        ### CONTACT KEYS PROCESSING
        # We get records from SF satisfying the filter in system parameter
        params = {
            'sfInstance':sfInstance,
            'priority':1,
            'externalObjName':'Contact',
            'sql':'SELECT Id, LastModifiedDate ' + self.env.ref('vcls-etl.etl_sf_contact_filter').value,
            'odooModelName':'res.partner',
            'is_full_update':is_full_update,
        }

        self.update_keys(params)

        
        

        #all_odoo = self.search([('externalObjName','in',['Contact','Account'])])



        """if to_reset and is_full_update:
            to_reset.write({'state':'upToDate'})
            _logger.info("ETL | {} keys reset".format(len(to_reset)))"""


        ###CLOSING
        self.env.user.context_data_integration = False

        
    """def updateAccountKey(self, externalInstance):
        sql = 'Select Id From Account'
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']

        for item in modifiedRecordsExt:
            odooAccount = self.env['etl.sync.keys'].search([('externalId','=',item['Id'])], limit=1)
            if odooAccount:
                odooAccount.write({'odooModelName':'res.partner','externalObjName':'Account'})
                #print("Update Key Account externalId :{}".format(item['Id']))
                #_logger.info("Update Key Account externalId :{}".format(item['Id']))


    def updateContactKey(self, externalInstance):
        sql =  'SELECT Id FROM Contact'
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']
        _logger.info("ETL | updateContactKey | \n {} \n  Found {} records".format(sql,len(modifiedRecordsExt)))

        for item in modifiedRecordsExt:
            odooContact = self.env['etl.sync.keys'].search([('externalId','=',item['Id'])], limit=1)
            if odooContact:
                odooContact.write({'odooModelName':'res.partner','externalObjName':'Contact'})
                #print("Update Key Contact externalId :{}".format(item['Id']))
                #_logger.info("Update Key Contact externalId :{}".format(item['Id']))

    def updateOpportunityKey(self, externalInstance):
        sql =  'SELECT Id '
        sql += 'FROM Opportunity'
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records']

        for item in modifiedRecordsExt:
            odooOpportunity = self.env['etl.sync.keys'].search([('externalId','=',item['Id'])], limit=1)
            if odooOpportunity:
                odooOpportunity.write({'odooModelName':'crm.lead','externalObjName':'Opportunity'})
                #print("Update Key Opportunity externalId :{}".format(item['Id']))
                #_logger.info("Update Key Opportunity externalId :{}".format(item['Id']))"""

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



