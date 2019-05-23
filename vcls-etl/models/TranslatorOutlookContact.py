from . import TranslatorSFGeneral

class TranslatorSFContact(TranslatorSFGeneral.TranslatorSFGeneral):
    def __init__(self,SF):
        super().__init__(SF)

    @staticmethod
    def translateToOdoo(Contact, odoo, SF):
        mapOdoo = odoo.env['map.odoo']
        result = {}
        if Contact['Title']:
            result['title'] = mapOdoo.convertRef(Contact['Title'], odoo,'res.partner.title',False)
        result['name'] = Contact['First Name'] + Contact['Last Name']
        #Contact['Sufix]
        #result['parent_id'] = Contact['Company"]


        result['stage'] = TranslatorSFContact.convertStatus(SF_Contact)
        # Ignore  Contact_Level__c
        # result['state_id'] = reference  BillingState
        if SF_Contact['MailingAddress']:
            result['city'] = SF_Contact['MailingAddress']['city']
            result['zip'] = SF_Contact['MailingAddress']['postalCode']
            result['street'] = SF_Contact['MailingAddress']['street']
        
        result['linkedin'] = SF_Contact['LinkedIn_Profile__c']
        result['phone'] = SF_Contact['Phone']
        result['fax'] = SF_Contact['Fax']
        result['mobile'] = SF_Contact['MobilePhone']
        result['email'] = SF_Contact['Email']

        # Ignore Area_of_expertise__c
        result['description'] = ''
        result['description'] += 'Contact description : ' + str(SF_Contact['Description']) + '\n'
        # Ignore Supplier_Selection_Form_completed__c
        result['website'] = SF_Contact['AccountWebsite__c']
        result['parent_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Contact['AccountId'],odoo)
        result['company_type'] = 'person'
        #documented to trigger proper default image loaded
        result['is_company'] = False
        
        if SF_Contact['MailingCountry']:
            result['country_id'] = mapOdoo.convertRef(SF_Contact['MailingCountry'],odoo,'res.country',False)
        
        result['currency_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Contact['CurrencyIsoCode'],odoo)        
        result['user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUserId(SF_Contact['OwnerId'],odoo, SF)
       
        result['category_id'] =  [(6, 0, TranslatorSFContact.convertCategory(SF_Contact, odoo))]
        if SF_Contact['Salutation']:
            result['title'] = mapOdoo.convertRef(SF_Contact['Salutation'], odoo,'res.partner.title',False)

        result['function'] = SF_Contact['Title']
        result['message_ids'] = [(0, 0, TranslatorSFContact.generateLog(SF_Contact))]

        if SF_Contact['Opted_In__c']:
            result['opted_in'] = SF_Contact['Opted_In__c']

        if SF_Contact['Unsubscribed_from_Marketing_Comms__c']:
            result['opted_out'] = True if SF_Contact['Unsubscribed_from_Marketing_Comms__c'] == 'Unsubscribed' else False

        if SF_Contact['VCLS_Initial_Contact__c']:
            result['vcls_contact_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUserId(SF_Contact['VCLS_Initial_Contact__c'],odoo, SF)

        if SF_Contact['VCLS_Main_Contact__c']:
            result['expert_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUserId(SF_Contact['VCLS_Main_Contact__c'],odoo, SF)

        return result