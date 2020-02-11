# -*- coding: utf-8 -*-

from odoo import models, fields, api

import datetime, pytz
from datetime import datetime,timedelta

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

    odooId = fields.Char(readonly = True,index=True)
    externalId = fields.Char(readonly = True,index=True)
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
    
    def open_con(self):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        return ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
    
    def update_keys(self,params={}):
        _logger.info("ETL | UPDATE KEYS {}".format(params))
        rec_ext = params['sfInstance'].getConnection().query_all(params['sql'])['records']
        keys_exist = self.search([('externalObjName','=',params['externalObjName']),('odooModelName','=',params['odooModelName'])])
        #we default the state of all keys
        keys_exist.write({'state':'upToDate','priority':0})
        keys_exist_sfid = keys_exist.mapped('externalId')
        keys_create = keys_exist.filtered(lambda k: k.externalId and not k.odooId)

        keys_update = self.env['etl.sync.keys']
        keys_to_test=keys_exist.filtered(lambda k: k.externalId and k.odooId)

        """if params['is_full_update']:
            keys_update = keys_exist.filtered(lambda k: k.externalId and k.odooId)
            keys_to_test = self.env['etl.sync.keys']
        else:
            keys_update = self.env['etl.sync.keys']
            #we fix those ones as ok by default
            keys_to_test=keys_exist.filtered(lambda k: k.externalId and k.odooId)
            keys_to_test.write({'state':'upToDate','priority':params['priority']})"""

        #We look for non exisitng keys
        for rec in rec_ext:
            if rec['Id'] not in keys_exist_sfid: #if the rec does not exists
                vals = {
                    'externalObjName':params['externalObjName'],
                    'externalId': rec['Id'],
                    'lastModifiedExternal': datetime.strptime(rec['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000"),
                    'odooModelName': params['odooModelName'],
                    'state':'needCreateOdoo',
                }
                keys_create |= self.create(vals)
                _logger.info("KEYS | New creation {}".format(vals))

            else: #we ensure not to try to update records we don't have in the rec
                key = keys_to_test.filtered(lambda k: k.externalId==rec['Id'])
                if key:
                    keys_update |= key         
                        
    
        if rec_ext:
            _logger.info("QUERY |\n{}\nreturned {} {} records".format(params['sql'],len(rec_ext),params['externalObjName']))
        if keys_exist:
            _logger.info("KEYS | Found {} existing keys of {}".format(len(keys_exist),params['externalObjName']))

        if keys_create:
            keys_create.write({'state':'needCreateOdoo','priority':params['priority']+1})
            _logger.info("KEYS | {} Keys to create".format(len(keys_create)))
        if keys_update:
            keys_update.write({'state':'needUpdateOdoo','priority':params['priority']})
            _logger.info("KEYS | {} Keys to update".format(len(keys_update)))   

    @api.model
    def sf_update_keys(self, is_full_update=True):
        """
        We 1st process the keys and priorities, starting from contacts.
        But then the queue must be executed in revert order of priorities to ensure parent accounts to be created 1st, etc.
        """
        ### PREPARATION
        #Update the context to execute vcls-rdd override
        self.env.user.context_data_integration = True
        #Clean the keys table of corrupted entries
        to_clean = self.search([('odooModelName','=',False)])
        #we also clean the ones to create in externals because we don't manage anymore this usecase
        to_clean |= self.search([('externalId','=',False)])
        for key in to_clean:
            key.unlink()
        
        #get instance
        sfInstance = self.open_con()

        #make time filter if required
        new_run = datetime.now(pytz.timezone("GMT"))
        if not is_full_update:
            last_run = self.env.ref('vcls-etl.ETL_LastRun').value
            formated_last_run = fields.Datetime.from_string(last_run).astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000")
            time_sql = " LastModifiedDate > {}".format(formated_last_run)
        else:
            time_sql = ""

        self.env.ref('vcls-etl.etl_sf_time_filter').value = time_sql
            

        ### CONTACT KEYS PROCESSING
        sql = """
            SELECT Id, LastModifiedDate FROM Contact
            """
        params = {
            'sfInstance':sfInstance,
            'priority':100,
            'externalObjName':'Contact',
            'sql':self.build_sql(sql,[self.env.ref('vcls-etl.etl_sf_contact_filter').value,time_sql]),
            'odooModelName':'res.partner',
            'is_full_update':is_full_update,
        }
        self.update_keys(params)

        ### ACCOUNT KEYS PROCESSING
        # We do accounts with parents 1st, because of their lower priority 
        sql = """
            SELECT Id, LastModifiedDate FROM Account 
                """
        params = {
            'sfInstance':sfInstance,
            'priority':200,
            'externalObjName':'Account',
            'sql': self.build_sql(sql,[self.env.ref('vcls-etl.etl_sf_account_filter').value,time_sql,'ParentId != null']),
            'odooModelName':'res.partner',
            'is_full_update':is_full_update,
        }
        self.update_keys(params)

        # then accounts without parents 
        sql = """
            SELECT Id, LastModifiedDate FROM Account 
            """
        params = {
            'sfInstance':sfInstance,
            'priority':300,
            'externalObjName':'Account',
            'sql': self.build_sql(sql,[self.env.ref('vcls-etl.etl_sf_account_filter').value,time_sql,'ParentId = null']),
            'odooModelName':'res.partner',
            'is_full_update':is_full_update,
        }
        self.update_keys(params)

        ### OPPORTUNITY KEYS PROCESSING
        sql = """
            SELECT Id, LastModifiedDate FROM Opportunity 
                """
        params = {
            'sfInstance':sfInstance,
            'priority':80,
            'externalObjName':'Opportunity',
            'sql': self.build_sql(sql,[self.env.ref('vcls-etl.etl_sf_opportunity_filter').value,time_sql]),
            'odooModelName':'crm.lead',
            'is_full_update':is_full_update,
        }
        self.update_keys(params)

        ### LEAD KEYS PROCESSING
        sql = """
            SELECT Id, LastModifiedDate FROM Lead 
            """
        params = {
            'sfInstance':sfInstance,
            'priority':60,
            'externalObjName':'Lead',
            'sql': self.build_sql(sql,[self.env.ref('vcls-etl.etl_sf_lead_filter').value,time_sql]),
            'odooModelName':'crm.lead',
            'is_full_update':is_full_update,
        }
        self.update_keys(params)

        ### CONTRACT KEYS PROCESSING
        #The one without parent contracts
        sql = """
            SELECT Id, LastModifiedDate FROM Contract
                """
        params = {
            'sfInstance':sfInstance,
            'priority':50,
            'externalObjName':'Contract',
            'sql': self.build_sql(sql,[self.env.ref('vcls-etl.etl_sf_contract_filter').value,time_sql,' Link_to_Parent_Contract__c = null']),
            'odooModelName':'agreement',
            'is_full_update':is_full_update,
        }
        self.update_keys(params)
        #The one with parent contracts
        sql = """
            SELECT Id, LastModifiedDate FROM Contract
                """
        params = {
            'sfInstance':sfInstance,
            'priority':40,
            'externalObjName':'Contract',
            'sql': self.build_sql(sql,[self.env.ref('vcls-etl.etl_sf_contract_filter').value,time_sql,' Link_to_Parent_Contract__c != null']),
            'odooModelName':'agreement',
            'is_full_update':is_full_update,
        }
        self.update_keys(params)

        ###CLOSING
        #we trigger the processing job
        cron = self.env.ref('vcls-etl.cron_process')
        cron.write({
            'active': True,
            'nextcall': datetime.now() + timedelta(seconds=30),
            'numbercall': 2,
        }) 

        self.env.ref('vcls-etl.ETL_LastRun').value = new_run.strftime("%Y-%m-%d %H:%M:%S.00+0000")
        self.env.user.context_data_integration = False
    
    def build_sql(self,core,filters=None):
        sql = core
        if filters:
            for fil in filters:
                if fil != "":
                    if 'WHERE' not in sql:
                        sql += " WHERE " + fil
                    else:
                        sql += " AND " + fil

        return sql

    @api.model
    def sf_process_keys(self,batch_size=False,loop=True):

        top_priority = max(self.search([('state','!=','upToDate')]).mapped('priority'))
        #priorities = list(set())
        #_logger.info("ETL |  {} ".format(priorities))

        if top_priority:
            #Init
            self.env.user.context_data_integration = True

            timestamp_end = datetime.now() + timedelta(minutes=1)
            loop_cron = loop

            sfInstance = self.open_con()
            
            if batch_size:
                to_process = self.search([('state','!=','upToDate'),('priority','=',top_priority)],limit=batch_size)
            else:
                to_process = self.search([('state','!=','upToDate'),('priority','=',top_priority)])
            
            if to_process:
                template = to_process[0]
                _logger.info("ETL | Found {} {} keys {} with priority {}".format(len(to_process),template.externalObjName,template.state,template.priority))
                #we initiate a sync object
                sync = self.env['etl.salesforce.{}'.format(template.externalObjName.lower())]
                translator = sync.getSFTranslator(sfInstance)
                counter = 0

                #get SF records
                query_id = "vcls-etl.etl_sf_{}_query".format(template.externalObjName.lower())
                filter_id = "vcls-etl.etl_sf_{}_filter".format(template.externalObjName.lower())
                sql = self.build_sql(self.env.ref(query_id).value,[self.env.ref(filter_id).value,self.env.ref("vcls-etl.etl_sf_time_filter").value])
                records = sfInstance.getConnection().query_all(sql)['records']
                if records:
                    _logger.info("ETL |  {} returned {} records from SF".format(sql,len(records)))
                    #we start the processing loop
                    for sf_rec in records:
                        if datetime.now()>timestamp_end:
                            break
                        else:
                            #grab the related key if in to_process
                            key = to_process.filtered(lambda p: p.externalId == sf_rec['Id'])
                            if key:
                                counter += 1
                                attributes = translator.translateToOdoo(sf_rec, sync, sfInstance)

                                #UPDATE Case
                                if key[0].state == 'needUpdateOdoo':
                                    #we catch the existing record
                                    o_rec = self.env[key[0].odooModelName].search([('id','=',key[0].odooId)],limit=1)
                                    if o_rec:
                                        o_rec.with_context(tracking_disable=1).write(attributes)
                                        key[0].write({'state':'upToDate','priority':0})
                                        _logger.info("ETL | Record Updated {}/{} | {} | {}".format(counter,len(to_process),key[0].externalObjName,attributes['name']))
                                    else:
                                        _logger.info("ETL | Missed Update - Odoo record not found {}/{} | {} | {}".format(counter,len(to_process),key[0].odooModelName,key[0].odooId))
                                
                                #CREATE Case
                                elif key[0].state == 'needCreateOdoo':
                                    odoo_id = self.env[key[0].odooModelName].with_context(tracking_disable=1).create(attributes).id
                                    key[0].write({'state':'upToDate','odooId':odoo_id,'priority':0})
                                    #key[0].write({'state':'upToDate','priority':0})
                                    _logger.info("ETL | Record Created {}/{} | {} | {}".format(counter,len(to_process),key[0].externalObjName,attributes['name']))
                                else:
                                    _logger.info("ETL | Non-managed key state {} | {}".format(key[0].id,key[0].state))
                                
            else:
                loop_cron = False
                _logger.info("ETL | Successful end of process.")

            #Close
            if loop_cron:
                cron = self.env.ref('vcls-etl.cron_relaunch')
                cron.write({
                    'active': True,
                    'nextcall': datetime.now() + timedelta(seconds=30),
                    'numbercall': 1,
                })
                _logger.info("ETL | CRON renewed")
            self.env.user.context_data_integration = False
    
    @api.model
    def relaunch_cron(self,external_id=None,numbercall=0):
        if external_id:
            cron = self.env.ref(external_id)
            if cron:
                cron.write({
                    'active': True,
                    'nextcall': datetime.now() + timedelta(seconds=10),
                    'numbercall': numbercall,
                })
                _logger.info("ETL | CRON relaunched")



        
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
        self.lastRun = fields.Datetime.from_string(datetime.now(pytz.timezone("GMT")).strftime("%Y-%m-%d %H:%M:%S.00+0000"))
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



