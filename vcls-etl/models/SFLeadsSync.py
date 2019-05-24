from . import TranslatorSFLeads
from . import ETL_SF
from . import generalSync

import pytz
from simple_salesforce import Salesforce
from tzlocal import get_localzone
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


from odoo import models, fields, api

class SFLeadsSync(models.Model):
    _name = 'etl.salesforce.leads'
    _inherit = 'etl.sync.mixin'

    def run(self,isFullUpdate, createInOdoo, updateInOdoo, nbMaxRecords):
        userSF = self.env.ref('vcls-etl.SF_mail').value
        passwordSF = self.env.ref('vcls-etl.SF_password').value
        token = self.env.ref('vcls-etl.SF_token').value
        sfInstance = ETL_SF.ETL_SF.getInstance(userSF, passwordSF, token)
        translator = TranslatorSFLeads.TranslatorSFLeads(sfInstance.getConnection())
        SF = self.env['etl.salesforce.leads'].search([])
        if not SF:
            SF = self.env['etl.salesforce.leads'].create({})
        
        isFinished = SF.updateKeyTable(sfInstance, isFullUpdate)
        
        cronName = 'etl salesforce opportunity'
        if isFullUpdate:
            cronName += ' full update'
        if isFinished :
            print('Updated key table done')
            if createInOdoo or updateInOdoo:
                SF.updateOdooInstance(translator,sfInstance, createInOdoo, updateInOdoo,nbMaxRecords)
            print('Updated odoo instance done')
            ##### CODE HERE #####
            SF.setNextRun()

            Cron = self.env['ir.cron'].search([('name','ilike','relauncher')])
            Cron.write({'active': False,'nextcall': datetime.now()})
        else:
            Cron = self.env['ir.cron'].with_context(active_test=False).search([('name','ilike','relauncher')]) 
            Cron.write({'active':True, 'name': 'relauncher {}'.format(cronName), 'nextcall': (datetime.now() + timedelta(seconds=15))})

    def updateKeyTable(self, externalInstance, isFullUpdate):
        # put logger here
        sql =  'SELECT Id, LastModifiedDate '
        sql += 'FROM Lead'

        if not isFullUpdate:
            sql += ' Where LastModifiedDate > ' + self.getStrLastRun().astimezone(pytz.timezone("GMT")).strftime("%Y-%m-%dT%H:%M:%S.00+0000") 
        print('Execute QUERY: {}'.format(sql))
        modifiedRecordsExt = externalInstance.getConnection().query_all(sql)['records'] # Get modified records in External Instance
        modifiedRecordsOdoo = self.env['crm.lead'].search([('write_date','>', self.getStrLastRun()),('type','=','lead')])
        
        j = 0
        i = 0 
        for extRecord in modifiedRecordsExt:
            if i < 200:
                try:
                    lastModifiedExternal = datetime.strptime(extRecord['LastModifiedDate'], "%Y-%m-%dT%H:%M:%S.000+0000").strftime("%Y-%m-%d %H:%M:%S.00+0000")
                    lastModifiedOdoo = self.getLastUpdate(self.toOdooId(extRecord['Id']))
                    
                    if isFullUpdate or not self.isDateOdooAfterExternal(lastModifiedOdoo, lastModifiedExternal):
                        # Exist in Odoo & External
                        # External is more recent
                        keyFromExt = self.getKeyFromExtId(extRecord['Id'])[0]
                        if keyFromExt.odooId:
                            keyFromExt.setState('needUpdateOdoo')
                            print('Update Key Table needUpdateOdoo, ExternalId :{}'.format(extRecord['Id']))
                        else:
                            keyFromExt.setState('needCreateOdoo')
                            print('Update Key Table needCreateOdoo, ExternalId :{}'.format(extRecord['Id']))
                        
                    else:
                        # Exist in Odoo & External
                        # Odoo is more recent
                        keyFromExt = self.getKeyFromExtId(extRecord['Id'])[0]
                        if keyFromExt.externalId:
                            keyFromExt.setState('needUpdateExternal')
                            print('Update Key Table needUpdateExternal, ExternalId :{}'.format(extRecord['Id']))
                        else:
                            keyFromExt.setState('needCreateExternal')
                            print('Update Key Table needCreateExternal, ExternalId :{}'.format(keyFromExt.externalId))
                except (generalSync.KeyNotFoundError, ValueError):
                    # Exist in External but not in Odoo
                    self.addKeys(externalId = extRecord['Id'], odooId = None, state = 'needCreateOdoo')
                    print('Update Key Table needCreateOdoo, ExternalId :{}'.format(extRecord['Id']))
                    i += 1
                j+=1
            else:
                break

        for odooRecord in modifiedRecordsOdoo:
            if i < 200:
                try:
                    key = self.getKeyFromOdooId(str(odooRecord.id))[0]
                    # Exist in Odoo & External
                    # Odoo is more recent
                    if key.state == 'upToDate':
                        key.setState('needUpdateExternal')
                        print('Update Key Table needUpdateExternal, OdooId :{}'.format(str(odooRecord.id)))
                except (generalSync.KeyNotFoundError, ValueError):
                    # Exist in Odoo but not in External
                    self.addKeys(externalId = None, odooId = str(odooRecord.id), state = 'needCreateExternal')
                    print('Update Key Table needCreateExternal, OdooId :{}'.format(str(odooRecord.id)))
                    i += 1
                j += 1
            else:
                break
        
        print(str(j%200)+' / '+str(len(modifiedRecordsExt) + len(modifiedRecordsOdoo)) )
        _logger.info(str(j%200)+' / '+str(len(modifiedRecordsExt) + len(modifiedRecordsOdoo)) )
        if j == (len(modifiedRecordsExt) + len(modifiedRecordsOdoo)):
            return True
        return False

    def updateOdooInstance(self, translator,externalInstance, createInOdoo, updateInOdoo, nbMaxRecords):
        sql = 'Select Id, Name, OwnerId, Activity__c, Address, City, Company, Content_Name__c, Country,PostalCode, Street, '
        sql += 'CurrencyIsoCode, Email,First_VCLS_Contact_Point__c, '
        sql += 'External_Referee__c, Fax, Functional_Focus__c, Inactive_Lead__c, Industry, Contact_us_Message__c, Initial_Product_Interest__c, '
        sql += 'LastModifiedDate, Title, Seniority__c, Phone, Website, Description, LeadSource From Lead'
        
        Modifiedrecords = externalInstance.getConnection().query_all(sql + ' ORDER BY Name')['records'] #All records
        if not nbMaxRecords:
            nbMaxRecords = len(self.keys)
        i = 0
        for key in self.keys:
            item = None
            if i < nbMaxRecords:
                if key.state == 'needUpdateOdoo' and updateInOdoo:
                    for record in Modifiedrecords:
                        if record['Id'] == key.externalId:
                            item = record
                    if item:
                        try:
                            odooAttributes = translator.translateToOdoo(item, self, externalInstance)
                            record = self.env['crm.lead'].search([('id','=',key.odooId)], limit=1)
                            record.write(odooAttributes)
                            print('Updated record in Odoo: {}'.format(item['Name']))
                            _logger.info('Updated record in Odoo: {}'.format(item['Name']))
                            key.state ='upToDate'
                            i += 1
                            print(str(i)+' / '+str(nbMaxRecords))
                        except ValueError as error:
                            _logger.error(error)
                elif key.state == 'needCreateOdoo' and createInOdoo:
                    for record in Modifiedrecords:
                        if record['Id'] == key.externalId:
                            item = record
                    if item:
                        odooAttributes = translator.translateToOdoo(item, self, externalInstance)
                        lead_id = self.env['crm.lead'].create(odooAttributes).id
                        print('Create new record in Odoo: {}'.format(item['Name']))
                        _logger.info('Create new record in Odoo: {}'.format(item['Name']))
                        key.odooId = lead_id
                        key.state ='upToDate'
                        i += 1
                        print(str(i)+' / '+str(nbMaxRecords))