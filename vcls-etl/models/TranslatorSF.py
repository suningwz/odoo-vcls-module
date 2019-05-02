from . import ITranslator

class TranslatorSF(ITranslator.ITranslator):
    
    @staticmethod
    def translateToOdoo(SF_Account, odoo, SF):
        result = {}
        # Modify the name with -test
        result['name'] = SF_Account['Name'] + '-test'

        # result['category_id'] = reference Supplier_Category__c
        result['stage'] = TranslatorSF.convertStatus(SF_Account['Supplier_Status__c'])
        # Ignore  Account_Level__c

        # result['state_id'] = reference  BillingState
        if SF_Account['BillingAddress']:
            result['city'] = SF_Account['BillingAddress']['city']
            result['zip'] = SF_Account['BillingAddress']['postalCode']
            result['street'] = SF_Account['BillingAddress']['street']
        
        result['phone'] = SF_Account['Phone']
        result['fax'] = SF_Account['Fax']
        # Ignore Area_of_expertise__c
        result['sharepoint_folder'] = TranslatorSF.convertUrl(SF_Account['Sharepoint_Folder__c']) # /!\
        result['description'] = ''
        result['description'] += 'Supplier description : ' + str(SF_Account['Supplier_Description__c']) + '\n'
        result['description'] += 'Key Information : {}\n'.format(SF_Account['Key_Information__c'])
        # Ignore Supplier_Selection_Form_completed__c
        result['website'] = SF_Account['Website']

        result['create_folder'] = SF_Account['Create_Sharepoint_Folder__c']
        result['company_type'] = 'company'
        result['country_id'] = TranslatorSF.convertCountry(SF_Account['BillingCountry'],odoo)
        result['user_id'] = TranslatorSF.convertAccountManager(SF_Account['OwnerId'],odoo, SF)
        result['category_id'] =  [(6, 0, TranslatorSF.convertCategory(SF_Account['Is_supplier__c'], SF_Account['Type'],odoo))]
    
        return result

    @staticmethod
    def translateToSF(Odoo_Account):
        """ inverse method waiting for implementation """
        pass

    @staticmethod
    def convertStatus(status):
        if status == 'Active - contract set up, information completed':
            return 5
        elif status == 'Prospective: no contract, pre-identify':
            return 2
        elif status == 'Inactive - reason mentioned':
            return 4
        else: # Undefined
            return 1
    
    @staticmethod
    def convertUrl(url):
        if url == "No link for this relationship":
            return None
        startIndex = url.find('http://')>0
        endIndex = url.find('target')-2
        return url[startIndex:endIndex]
    
    @staticmethod
    def convertCountry(country,odoo):
        if country == None:
            return None
        elif 'argentina' in country.lower() or country.lower() == ('arg') :
            return odoo.env.ref('base.ar').id
        elif 'australia' in country.lower() or country.lower() == ('au') :
            return odoo.env.ref('base.au').id
        elif 'belgium' in country.lower() or country.lower() == ('be') :
            return odoo.env.ref('base.be').id
        elif 'brazil' in country.lower() or country.lower() == ('bra') :
            return odoo.env.ref('base.br').id
        elif 'canada' in country.lower() or country.lower() == ('ca') :
            return odoo.env.ref('base.ca').id
        elif 'china' in country.lower() or country.lower() == ('cn') :
            return odoo.env.ref('base.cn').id
        elif 'croatia' in country.lower() or country.lower() == ('hr') :
            return odoo.env.ref('base.hr').id
        elif 'czech republic' in country.lower() or country.lower() == ('cz') :
            return odoo.env.ref('base.cz').id
        elif 'denmark' in country.lower() or country.lower() == ('dk') :
            return odoo.env.ref('base.dk').id
        elif 'egypt' in country.lower() or country.lower() == ('eg') :
            return odoo.env.ref('base.eg').id
        elif 'france' in country.lower() or country.lower() == ('fr') :
            return odoo.env.ref('base.fr').id
        elif 'germany' in country.lower() or country.lower() == ('de') :
            return odoo.env.ref('base.de').id
        elif 'greece' in country.lower() or country.lower() == ('gr') :
            return odoo.env.ref('base.gr').id
        elif 'hong kong' in country.lower() or country.lower() == ('hk') :
            return odoo.env.ref('base.hk').id
        elif 'india' in country.lower() or country.lower() == ('in') :
            return odoo.env.ref('base.in').id
        elif 'ireland' in country.lower() or country.lower() == ('ie') :
            return odoo.env.ref('base.ie').id
        elif 'israel' in country.lower() or country.lower() == ('il') :
            return odoo.env.ref('base.il').id
        elif 'italy' in country.lower() or country.lower() == ('it') :
            return odoo.env.ref('base.it').id
        elif 'japan' in country.lower() or country.lower() == ('jp') :
            return odoo.env.ref('base.jp').id
        elif 'jordan' in country.lower() or country.lower() == ('jo') :
            return odoo.env.ref('base.jo').id
        elif 'korea' in country.lower() or country.lower() == ('kr') :
            return odoo.env.ref('base.kr').id
        elif 'lithuania' in country.lower() or country.lower() == ('lt') :
            return odoo.env.ref('base.lt').id
        elif 'netherlands' in country.lower() or country.lower() == ('nl') :
            return odoo.env.ref('base.nl').id
        elif 'norway' in country.lower() or country.lower() == ('no') :
            return odoo.env.ref('base.no').id
        elif 'poland' in country.lower() or country.lower() == ('pl') :
            return odoo.env.ref('base.pl').id
        elif 'portugal' in country.lower() or country.lower() == ('pt') :
            return odoo.env.ref('base.pt').id
        elif 'singapore' in country.lower() or country.lower() == ('sg') :
            return odoo.env.ref('base.sg').id
        elif 'south africa' in country.lower() or country.lower() == ('za') :
            return odoo.env.ref('base.za').id
        elif 'spain' in country.lower() or country.lower() == ('es') :
            return odoo.env.ref('base.es').id
        elif 'sweden' in country.lower() or country.lower() == ('se') :
            return odoo.env.ref('base.se').id
        elif 'switzerland' in country.lower() or country.lower() == ('ch') :
            return odoo.env.ref('base.ch').id
        elif 'turkey' in country.lower() or country.lower() == ('ch') :
            return odoo.env.ref('base.ch').id
        elif 'united kingdom' in country.lower() or country.lower() == ('uk') in country.lower() or country.lower() == ('u.k.') :
            return odoo.env.ref('base.uk').id
        elif 'united arab emirates' in country.lower() or country.lower() == ('ae') :
            return odoo.env.ref('base.ae').id
        elif 'us' :
            return odoo.env.ref('base.us').id
        else:
            return None
    
    @staticmethod
    def convertAccountManager(ownerId, odoo, SF):
        mail = TranslatorSF.getUserMail(ownerId,SF)
        return TranslatorSF.getUserId(mail,odoo)

    @staticmethod
    def convertCategory(isSupplier, SFtype, odoo):
        result = []
        if isSupplier:
            result += [odoo.env.ref('vcls-contact.category_PS').id]
        if SFtype:
            if (not isSupplier) and 'supplier' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_PS').id]
            if 'competitor' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_competitor').id]
            if 'partner' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_partner').id]
        return result
    
    @staticmethod
    def getUserMail(userId, SF):
        userIdString = "'{}'".format(userId)
        queryUser = "Select Username FROM User Where Id = {}".format(userIdString)
        result = SF.query(queryUser)['records']
        return result[0]['Username']

    @staticmethod
    def getUserId(mail, odoo):
        result = odoo.env['res.users'].search([('email','=',mail)])
        if result:
            return result[0]
        else:
            return None