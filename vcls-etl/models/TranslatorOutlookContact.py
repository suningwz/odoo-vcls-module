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
        #Contact['Sufix']
        #result['parent_id'] = Contact['Company"]
        #Contcat['Department'] Paris OR RENNES
        result['function'] = Contact['Job Title']
        result['street'] = Contact['Business Street']
        result['city'] = Contact['Business City']
        result['state'] = Contact['Business State']
        result['zip'] = Contact['Business Postal Code']
        if Contact['Business Country/Region']:
            result['country_id'] = mapOdoo.convertRef(Contact['Business Country/Region'],odoo,'res.country',False)
        result['description'] = 'Home Address : ' + Contact['Home Street'] 
        + Contact['Home City'] + Contact['Home State'] + Contact['Home Postal Code']
        + Contact['Home Country']
        result['description'] += 'Other Address : ' + Contact['Other Street'] + Contact['Other City'] +Contact['Other Country/Region']
        result['fax'] = Contact['Business Fax']
        result['phone'] = Contact['Business Phone']
        Contact['Business Phone2']
        Contact['Home Phone']
        Contact['Home Phone2']
        Contact['Mobile Phone']
        Contact['Other Fax']
        Contact['Other Phone']
        Contact['Pager']
        Contact['Categories']
        result['email'] = Contact['E-mail Address']
        Contact['E-mail 2 Address']
        Contact['E-mail 3 Address']
        Contact['Initials']
        Contact["Manager's Name"]
        Contact['description'] += Contact['Notes']
        result['website'] = Contact['Web Page']


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