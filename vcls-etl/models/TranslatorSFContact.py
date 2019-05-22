from . import TranslatorSFGeneral

class TranslatorSFContact(TranslatorSFGeneral.TranslatorSFGeneral):
    def __init__(self,SF):
        super().__init__(SF)

    @staticmethod
    def translateToOdoo(SF_Contact, odoo, SF):
        mapOdoo = odoo.env['map.odoo']
        result = {}
        # Modify the name with -test
        result['name'] = SF_Contact['Name'] #+ '-test'
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
    
    @staticmethod
    def generateLog(SF_Contact):
        result = {
            'model': 'res.partner',
            'message_type': 'comment',
            'body': '<p>Updated.</p>'
        }

        return result

    @staticmethod
    def translateToSF(Odoo_Contact, odoo):
        result = {}
        # Modify the name with -test
        if ' ' in Odoo_Contact.name:
            name = Odoo_Contact.name.split(' ')
            if len(name)>2:
                result['lastName'] = Odoo_Contact.name
            else:
                result['FirstName'], result['lastName'] = name
        else:
            result['lastName'] = Odoo_Contact.name
        if Odoo_Contact.city:
            result['MailingCity'] = Odoo_Contact.city
        if Odoo_Contact.zip:
            result['MailingPostalCode'] = Odoo_Contact.zip
        if Odoo_Contact.street:
            result['MailingStreet'] = Odoo_Contact.street
        if Odoo_Contact.phone:
            result['Phone'] = Odoo_Contact.phone
        if Odoo_Contact.fax:
            result['Fax'] = Odoo_Contact.fax
        if Odoo_Contact.mobile:
            result['MobilePhone'] = Odoo_Contact.mobile
        if '@' in str(Odoo_Contact.email):
            result['Email'] = Odoo_Contact.email
        if Odoo_Contact.description:
            result['Description'] = Odoo_Contact.description
        result['AccountId'] = TranslatorSFContact.toSfId(Odoo_Contact.parent_id.id,odoo)
        
        # Ignore company_type
        result['MailingCountry'] = TranslatorSFContact.revertCountry(Odoo_Contact.country_id.id, odoo)
        result['CurrencyIsoCode'] = Odoo_Contact.currency_id.name
        result['OwnerId'] = TranslatorSFContact.revertOdooIdToSfId(Odoo_Contact.user_id,odoo)
        """ for c in Odoo_Contact.category_id:
            category += c.name 
        result['Category__c'] = category""" 
        result['Salutation'] = TranslatorSFContact.revertSalutation(Odoo_Contact.title.name, odoo)
        result['Title'] = Odoo_Contact.function


        return result

    @staticmethod
    def convertStatus(SF):
        if SF['Inactive_Contact__c']:
            return 5
        else: # New
            return 2
    
    @staticmethod
    def revertStatus(status):
        if status == 3:
            return 'Active - contract set up, information completed'
        elif status == 2:
            return 'Prospective: no contract, pre-identify'
        elif status == 5:
            return 'Inactive - reason mentioned'
        else: # Undefined
            return 'Undefined - to fill'

    @staticmethod
    def convertCategory(SF, odoo):
        result = []
        if SF['Supplier__c']:
            result += [odoo.env.ref('vcls-contact.category_PS').id]
        """ if SFtype:
            if (not isSupplier) and 'supplier' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_PS').id]
            if 'competitor' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_competitor').id]
            if 'partner' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_partner').id] """
        return result
    @staticmethod
    def revertSalutation(OdooSalutation, odoo):
        return odoo.env['res.partner.title'].search([('name','ilike',OdooSalutation)])