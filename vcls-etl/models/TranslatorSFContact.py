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
        result['country_id'] = TranslatorSFContact.convertCountry(SF_Contact['MailingCountry'],odoo)
        result['currency_id'] = TranslatorSFContact.convertCurrency(SF_Contact['CurrencyIsoCode'],odoo)
        
        result['user_id'] = TranslatorSFContact.convertSfIdToOdooId(SF_Contact['OwnerId'],odoo, SF)
       
        result['category_id'] =  [(6, 0, TranslatorSFContact.convertCategory(SF_Contact['Supplier__c'],SF_Contact['Category__c'],odoo))]
    
        result['title'] = TranslatorSFContact.convertSalutation(SF_Contact['Salutation'], odoo)

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
    def test(word):
        print(word)
        return word.replace("-test","")

    @staticmethod
    def translateToSF(Odoo_Contact, odoo):
        result = {}
        # Modify the name with -test
        result['Name'] = TranslatorSFContact.test(Odoo_Contact.name)
        print(result['Name'])

        #result['Supplier_Status__c'] = TranslatorSFContact.revertStatus(Odoo_Contact.stage)

        '''
        if SF_Contact['BillingAddress']:
            result['city'] = SF_Contact['BillingAddress']['city']
            result['zip'] = SF_Contact['BillingAddress']['postalCode']
            result['street'] = SF_Contact['BillingAddress']['street']
        '''

        result['Phone'] = Odoo_Contact.phone
        result['Fax'] = Odoo_Contact.fax
        # result['Sharepoint_Folder__c'] = TranslatorSFContact.revertUrl(Odoo_Contact.sharepoint_folder)
        # Ignore description
        result['Website'] = Odoo_Contact.website

        # Ignore company_type
        result['BillingCountry'] = TranslatorSFContact.revertCountry(Odoo_Contact.country_id.id, odoo)
        # result['user_id'] = TranslatorSFContact.convertSfIdToOdooId(SF_Contact['OwnerId'],odoo, SF)
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
    def convertCountry(country,odoo):
        if country:
            countrylower = country.lower()
            if 'argentina' in countrylower or countrylower == ('arg') :
                return odoo.env.ref('base.ar').id
            elif 'australia' in countrylower or countrylower == ('au') :
                return odoo.env.ref('base.au').id
            elif 'belgium' in countrylower or countrylower == ('be') :
                return odoo.env.ref('base.be').id
            elif 'brazil' in countrylower or countrylower == ('bra') :
                return odoo.env.ref('base.br').id
            elif 'canada' in countrylower or countrylower == ('ca') :
                return odoo.env.ref('base.ca').id
            elif 'china' in countrylower or countrylower == ('cn') :
                return odoo.env.ref('base.cn').id
            elif 'croatia' in countrylower or countrylower == ('hr') :
                return odoo.env.ref('base.hr').id
            elif 'czech republic' in countrylower or countrylower == ('cz') :
                return odoo.env.ref('base.cz').id
            elif 'denmark' in countrylower or countrylower == ('dk') :
                return odoo.env.ref('base.dk').id
            elif 'egypt' in countrylower or countrylower == ('eg') :
                return odoo.env.ref('base.eg').id
            elif 'france' in countrylower or countrylower == ('fr') :
                return odoo.env.ref('base.fr').id
            elif 'germany' in countrylower or countrylower == ('de') :
                return odoo.env.ref('base.de').id
            elif 'greece' in countrylower or countrylower == ('gr') :
                return odoo.env.ref('base.gr').id
            elif 'hong kong' in countrylower or countrylower == ('hk') :
                return odoo.env.ref('base.hk').id
            elif 'india' in countrylower or countrylower == ('in') :
                return odoo.env.ref('base.in').id
            elif 'ireland' in countrylower or countrylower == ('ie') :
                return odoo.env.ref('base.ie').id
            elif 'israel' in countrylower or countrylower == ('il') :
                return odoo.env.ref('base.il').id
            elif 'italy' in countrylower or countrylower == ('it') :
                return odoo.env.ref('base.it').id
            elif 'japan' in countrylower or countrylower == ('jp') :
                return odoo.env.ref('base.jp').id
            elif 'jordan' in countrylower or countrylower == ('jo') :
                return odoo.env.ref('base.jo').id
            elif 'korea' in countrylower or countrylower == ('kr') :
                return odoo.env.ref('base.kr').id
            elif 'lithuania' in countrylower or countrylower == ('lt') :
                return odoo.env.ref('base.lt').id
            elif 'netherlands' in countrylower or countrylower == ('nl') :
                return odoo.env.ref('base.nl').id
            elif 'norway' in countrylower or countrylower == ('no') :
                return odoo.env.ref('base.no').id
            elif 'poland' in countrylower or countrylower == ('pl') :
                return odoo.env.ref('base.pl').id
            elif 'portugal' in countrylower or countrylower == ('pt') :
                return odoo.env.ref('base.pt').id
            elif 'singapore' in countrylower or countrylower == ('sg') :
                return odoo.env.ref('base.sg').id
            elif 'south africa' in countrylower or countrylower == ('za') :
                return odoo.env.ref('base.za').id
            elif 'spain' in countrylower or countrylower == ('es') :
                return odoo.env.ref('base.es').id
            elif 'sweden' in countrylower or countrylower == ('se') :
                return odoo.env.ref('base.se').id
            elif 'switzerland' in countrylower or countrylower == ('ch') :
                return odoo.env.ref('base.ch').id
            elif 'turkey' in countrylower or countrylower == ('ch') :
                return odoo.env.ref('base.ch').id
            elif 'united kingdom' in countrylower or countrylower == ('uk') in countrylower or countrylower == ('u.k.') :
                return odoo.env.ref('base.uk').id
            elif 'united arab emirates' in countrylower or countrylower == ('ae') :
                return odoo.env.ref('base.ae').id
            elif 'us' in countrylower:
                return odoo.env.ref('base.us').id
            elif 'cayman islands' in countrylower or countrylower == ('ky'):
                return odoo.env.ref('base.ky').id
            elif 'united states' in countrylower or countrylower == ('us'):
                return odoo.env.ref('base.us').id
            elif 'slovakia' in countrylower or countrylower == ('sk'):
                return odoo.env.ref('base.sk').id
            elif 'finland' in countrylower or countrylower == ('fi'):
                return odoo.env.ref('base.fi').id
            elif 'suisse' in countrylower or countrylower == ('ch'):
                return odoo.env.ref('base.ch').id
            elif 'uk' in countrylower or countrylower == ('uk'):
                return odoo.env.ref('base.uk').id
            elif 'iceland' in countrylower or countrylower == ('is'):
                return odoo.env.ref('base.is').id
            elif 'luxembourg' in countrylower or countrylower == ('lu'):
                return odoo.env.ref('base.lu').id
            elif 'thailand' in countrylower or countrylower == ('th'):
                return odoo.env.ref('base.th').id
            elif 'vietnam' in countrylower or countrylower == ('vn'):
                return odoo.env.ref('base.vn').id
            elif 'bulgaria' in countrylower or countrylower == ('bg'):
                return odoo.env.ref('base.bg').id
            elif 'u.K' in countrylower:
                return odoo.env.ref('base.uk').id
            elif 'netherland' in countrylower or countrylower == ('nl'):
                return odoo.env.ref('base.nl').id
            elif 'belgique' in countrylower or countrylower == ('be'):
                return odoo.env.ref('base.be').id
        return None

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
    def toOdooId(externalId, odoo):
        for key in odoo.env['etl.salesforce.account'].search([]).keys:
            if key.externalId == externalId:
                return key.odooId
        return None
    @staticmethod
    def convertCurrency(SfCurrency,odoo):
        odooCurr = odoo.env['res.currency'].search([('name','=',SfCurrency)]).id
        if odooCurr:
            return odooCurr
        else:
            return None