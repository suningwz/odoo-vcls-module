from . import TranslatorSFGeneral

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
        result['user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertSfIdToOdooId(SF_Leads['OwnerId'],odoo,SF)
        result['description'] = ''
        if SF_Leads['Description']:
            result['description'] +='Description : ' + str(SF_Leads['Description']) + '\n'
        if SF_Leads['LeadSource']:
            result['source_id'] = mapOdoo.convertRef(SF_Leads['LeadSource'],odoo,'utm.source',False)
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
        
        #result[''] = SF_Leads['Company']
        #Content_Name__c
        result['company_currency'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Leads['CurrencyIsoCode'],odoo)
        result['user_email'] = SF_Leads['Email']
        #First_VCLS_Contact_Point__c
        #result['referent_id'] = SF_Leads['External_Referee__c']
        #fax
        result['functional_focus_id'] = SF_Leads['Functional_Focus__c']
        #Inactive_Lead__c
        if SF_Leads['Industry']:
            result['industry_id'] = mapOdoo.convertRef(SF_Leads['Industry'],odoo,'res.partner.industry',False)
        #Contact_us_Message__c
        result['function'] = SF_Leads['Title']
        if SF_Leads['Seniority__c']:
            result['partner_seniority_id'] = mapOdoo.convertRef(SF_Leads['Seniority__c'], odoo,'res.country',False)
        result['message_ids'] = [(0, 0, TranslatorSFLeads.generateLog(SF_Leads))]


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
    