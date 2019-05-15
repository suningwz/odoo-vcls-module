from . import ITranslator

class KeyNotFoundError(Exception):
    pass

class TranslatorSFContact(ITranslator.ITranslator):

    def __init__(self,SF):
        queryUser = "Select Username,Id FROM User"
        TranslatorSFContact.usersSF = SF.query(queryUser)['records']
    
    @staticmethod
    def translateToOdoo(SF_Contact, odoo, SF):
        result = {}
        # Modify the name with -test
        result['name'] = SF_Contact['Name'] #+ '-test'

        # result['category_id'] = reference Supplier_Category__c
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
        result['parent_id'] = TranslatorSFContact.toOdooId(SF_Contact['AccountId'],odoo)
        result['company_type'] = 'person'
        #documented to trigger proper default image loaded
        result['is_company'] = False
        if SF_Contact['MailingCountry']:
            result['country_id'] = TranslatorSFContact.convertId(SF_Contact['MailingCountry'],odoo,'res.country',False)
        result['currency_id'] = TranslatorSFContact.convertCurrency(SF_Contact['CurrencyIsoCode'],odoo)
        
        result['user_id'] = TranslatorSFContact.convertSfIdToOdooId(SF_Contact['OwnerId'],odoo, SF)
       
        result['category_id'] =  [(6, 0, TranslatorSFContact.convertCategory(SF_Contact['Supplier__c'],SF_Contact['Category__c'],odoo))]
        if SF_Contact['Salutation']:
            result['title'] = TranslatorSFContact.convertId(SF_Contact['Salutation'], odoo,'res.partner.title',False)

        result['function'] = SF_Contact['Title']
        result['message_ids'] = [(0, 0, TranslatorSFContact.generateLog(SF_Contact))]

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
        result['Name'] = Odoo_Contact.name
        print(result['Name'])

        #result['Supplier_Status__c'] = TranslatorSFContact.revertStatus(Odoo_Contact.stage)
        result['MailingAddress'] = {}
        result['MailingAddress']['city'] = Odoo_Contact.city
        result['MailingAddress']['postalCode'] = Odoo_Contact.zip
        result['MailingAddress']['street'] = Odoo_Contact.street
        result['Phone'] = Odoo_Contact.phone
        result['Fax'] = Odoo_Contact.fax
        result['MobilePhone'] = Odoo_Contact.mobile
        result['Email'] = Odoo_Contact.email
        result['Description'] = Odoo_Contact.description
        result['AccountWebsite__c'] = Odoo_Contact.website
        result['AccountId'] = TranslatorSFContact.toSfId(Odoo_Contact.parent_id.id,odoo)
        # Ignore company_type
        result['MailingCountry'] = TranslatorSFContact.revertCountry(Odoo_Contact.country_id.id, odoo)
        result['CurrencyIsoCode'] = Odoo_Contact.currency_id.name
        result['OwnerId'] = TranslatorSFContact.revertOdooIdToSfId(Odoo_Contact.user_id,odoo)
        """ for c in Odoo_Contact.category_id:
            category += c.name 
        result['Category__c'] = category""" 
        result['Salutation'] = TranslatorSFContact.revertSalutation(Odoo_Contact.title)
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
    def convertUrl(url):
        if url == "No link for this relationship":
            return None
        startIndex = url.find('http://')>0
        endIndex = url.find('target')-2
        return url[startIndex:endIndex]
    
    @staticmethod
    def revertUrl(url):
        if not url:
            return "No link for this relationship"
        else:
            return '<a href="{}" target="_blank">Supplier Folder</a>'.format(url)
    
    @staticmethod
    def revertCountry(country, odoo):
        if country:
            return odoo.env['res.country'].browse(country).name
        return None

    @staticmethod
    def convertSfIdToOdooId(ownerId, odoo, SF):
        mail = TranslatorSFContact.getUserMail(ownerId,SF)
        return TranslatorSFContact.getUserId(mail,odoo)
    @staticmethod
    def revertOdooIdToSfId(idodoo,odoo):
        mail = TranslatorSFContact.getUserMailOd(idodoo.id,odoo)
        return TranslatorSFContact.getUserIdSf(mail)
    @staticmethod
    def convertCategory(isSupplier, SFtype, odoo):
        result = []
        if isSupplier:
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
    def getUserMail(userId, SF):
        for user in TranslatorSFContact.usersSF:
            if user['Id'] == userId:
                return user['Username']
            else:
                return None

    @staticmethod
    def getUserId(mail, odoo):
        result = odoo.env['res.users'].search([('email','=',mail)])
        if result:
            return result[0].id
        else:
            return None
    @staticmethod
    def getUserIdSf(mail):
        for user in TranslatorSFContact.usersSF:
            if user['Username'] == mail:
                return user['Id']
            else:
                return None
    @staticmethod
    def getUserMailOd(userId,odoo):
        result = odoo.env['res.users'].search([('id','=',userId)])
        if result:
            return result[0].email
        else:
            return None

    @staticmethod
    def convertSalutation(SFSalutation, odoo):
        if SFSalutation:
            if 'mr' in SFSalutation.lower():
                return odoo.env.ref('base.res_partner_title_mister').id
            if 'dr' in SFSalutation.lower():
                return odoo.env.ref('base.res_partner_title_doctor').id
            if 'ms' in SFSalutation.lower():
                return odoo.env.ref('base.res_partner_title_miss').id
            if 'mrs' in SFSalutation.lower():
                return odoo.env.ref('base.res_partner_title_madam').id
            if 'prof' in SFSalutation.lower():
                return odoo.env.ref('base.res_partner_title_prof').id
    @staticmethod
    def revertSalutation(OdooSalutation):
        if OdooSalutation:
            if 'mister' in OdooSalutation.lower():
                return 'mr'
            if 'doctor' in OdooSalutation.lower():
                return 'dr'
            if 'miss' in OdooSalutation.lower():
                return 'ms'
            if 'madam' in OdooSalutation.lower():
                return 'mrs' 
            if 'prof' in OdooSalutation.lower():
                return 'prof'

    @staticmethod
    def toOdooId(externalId, odoo):
        for key in odoo.env['etl.salesforce.account'].search([]).keys:
            if key.externalId == externalId:
                return key.odooId
        return None
    @staticmethod
    def toSfId(odooId,odoo):
        for key in odoo.env['etl.salesforce.account'].search([]).keys:
            if key.odooId == odooId:
                return key.externalId
        return None
    @staticmethod
    def convertCurrency(SfCurrency,odoo):
        odooCurr = odoo.env['res.currency'].search([('name','=',SfCurrency)]).id
        if odooCurr:
            return odooCurr
        else:
            return None