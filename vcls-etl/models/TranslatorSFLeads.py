from . import TranslatorSFGeneral
import logging
_logger = logging.getLogger(__name__)

class KeyNotFoundError(Exception):
    pass

class TranslatorSFLeads(TranslatorSFGeneral.TranslatorSFGeneral):
    def __init__(self,SF):
        super().__init__(SF)
    
    @staticmethod
    def translateToOdoo(SF_Leads, odoo, SF):
        mapOdoo = odoo.env['map.odoo']
        result = {}
        result['name'] = SF_Leads['Name']
        if SF_Leads['Salutation']:
            result['title'] = mapOdoo.convertRef(SF_Leads['Salutation'], odoo,'res.partner.title',False)
        if SF_Leads['OwnerId']:
            result['user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertSfIdToOdooId(SF_Leads['OwnerId'],odoo,SF)
        result['description'] = ''
        if SF_Leads['Description']:
            result['description'] += 'Description : ' + str(SF_Leads['Description']) + '\n'
        if SF_Leads['LeadSource']:
            result['marketing_project_id'] = mapOdoo.convertRef(SF_Leads['LeadSource'],odoo,'project.project',False)
        result['type'] = 'lead'

        if SF_Leads['Activity__c']:
            result['client_activity_ids'] =  [(6, 0, mapOdoo.convertRef(SF_Leads['Activity__c'],odoo,'client.activity',True))]
        if SF_Leads['Initial_Product_Interest__c']:
            result['client_product_ids'] = [(6, 0, mapOdoo.convertRef(SF_Leads['Initial_Product_Interest__c'],odoo,'client.product',True))]
        
        result['phone'] = SF_Leads['Phone']
        result['website'] =  SF_Leads['Website']
        result['city'] = SF_Leads['City']
        result['zip'] = SF_Leads['PostalCode']
        result['street'] = SF_Leads['Street']
        if SF_Leads['Country']:
            result['country_id'] = mapOdoo.convertRef(SF_Leads['Country'],odoo,'res.country',False)
        if SF_Leads['State']:
            result['state_id'] = mapOdoo.convertRef(SF_Leads['State'],odoo,'res.country.state',False)
        if SF_Leads['Status']:
            result['lead_stage_id'] = mapOdoo.convertRef(SF_Leads['Status'],odoo,'crm.lead.stage',False)

        result['partner_name'] = SF_Leads['Company']

        #Content_Name__c

        result['customer_currency_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Leads['CurrencyIsoCode'],odoo)
        result['user_email'] = SF_Leads['Email']
        if SF_Leads['First_VCLS_Contact_Point__c']:
            result['initial_vcls_contact'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Leads['First_VCLS_Contact_Point__c'],"res.partner","Contact", odoo)
        if SF_Leads['External_Referee__c']:
            result['referent_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Leads['External_Referee__c'], "res.partner", "Contact", odoo)
        #fax
        if SF_Leads['Functional_Focus__c']:
            result['functional_focus_id'] = mapOdoo.convertRef(SF_Leads['Functional_Focus__c'],odoo,'partner.functional.focus',False)
        #Inactive_Lead__c
        if SF_Leads['Industry']:
            result['industry_id'] = mapOdoo.convertRef(SF_Leads['Industry'],odoo,'res.partner.industry',False)
        result['contact_us_message'] = SF_Leads['Contact_us_Message__c']
        result['function'] = SF_Leads['Title']
        if SF_Leads['Seniority__c']:
            result['partner_seniority_id'] = mapOdoo.convertRef(SF_Leads['Seniority__c'], odoo,'partner.seniority',False)
        result['message_ids'] = [(0, 0, TranslatorSFLeads.generateLog(SF_Leads))]

        #_logger.info("TRANSLATOR LEAD {}".format(result))
        if SF_Leads['Opt_in_Campaign__c']:
            result['marketing_task_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Leads['Opt_in_Campaign__c'],"project.task","Campaign",odoo)
        if SF_Leads['Unsubscribe_Campaign__c']:
            result['marketing_task_out_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Leads['Unsubscribe_Campaign__c'],"project.task","Campaign",odoo)
        result['conversion_date'] = SF_Leads['ConvertedDate']
        if SF_Leads['LinkedIn_Profile__c']:
            result['linkedin_url'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUrl(SF_Leads['LinkedIn_Profile__c'])
        if SF_Leads['Opted_In__c']:
            result['opted_in'] = SF_Leads['Opted_In__c']
        

        return result
    
    @staticmethod
    def generateLog(SF_Leads):
        result = {
            'model': 'crm.lead',
            'message_type': 'comment',
            'body': '<p>Updated.</p>'
        }

        return result
    @staticmethod
    def translateToSF(Odoo_Account):
        pass
    