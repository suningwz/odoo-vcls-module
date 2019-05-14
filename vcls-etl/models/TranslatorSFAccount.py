from . import ITranslator

class TranslatorSFAccount(ITranslator.ITranslator):
    def __init__(self,SF):
        queryUser = "Select Username,Id FROM User"
        TranslatorSFAccount.usersSF = SF.query(queryUser)['records']
    @staticmethod
    def translateToOdoo(SF_Account, odoo, SF):
        result = {}
        # Modify the name with -test
        result['name'] = SF_Account['Name'] #+ '-test'

        # result['category_id'] = reference Supplier_Category__c
        result['stage'] = TranslatorSFAccount.convertStatus(SF_Account)
        # Ignore  Account_Level__c

        # result['state_id'] = reference  BillingState
        if SF_Account['BillingAddress']:
            result['city'] = SF_Account['BillingAddress']['city']
            result['zip'] = SF_Account['BillingAddress']['postalCode']
            result['street'] = SF_Account['BillingAddress']['street']
        
        result['phone'] = SF_Account['Phone']
        result['fax'] = SF_Account['Fax']
        # Ignore Area_of_expertise__c
        result['sharepoint_folder'] = TranslatorSFAccount.convertUrl(SF_Account['Sharepoint_Folder__c']) # /!\
        result['description'] = ''
        result['description'] += 'Supplier description : ' + str(SF_Account['Supplier_Description__c']) + '\n'
        result['description'] += 'Key Information : {}\n'.format(SF_Account['Key_Information__c'])
        # Ignore Supplier_Selection_Form_completed__c
        result['website'] = SF_Account['Website']

        result['create_folder'] = SF_Account['Create_Sharepoint_Folder__c']
        result['company_type'] = 'company'
        #documented to trigger proper default image loaded
        result['is_company'] = 'True'
        result['country_id'] = TranslatorSFAccount.convertCountry(SF_Account['BillingCountry'],odoo)

        result['currency_id'] = TranslatorSFAccount.convertCurrency(SF_Account['CurrencyIsoCode'],odoo)
        result['user_id'] = TranslatorSFAccount.convertSfIdToOdooId(SF_Account['OwnerId'],odoo, SF)
        if SF_Account['Main_VCLS_Contact__c']:
            result['expert_id'] = TranslatorSFAccount.convertSfIdToOdooId(SF_Account['Main_VCLS_Contact__c'],odoo, SF)
        if SF_Account['Project_Assistant__c']:
            result['assistant_id'] = TranslatorSFAccount.convertSfIdToOdooId(SF_Account['Project_Assistant__c'],odoo, SF)
        if SF_Account['Project_Controller__c']:
            result['controller_id'] = TranslatorSFAccount.convertSfIdToOdooId(SF_Account['Project_Controller__c'],odoo, SF)

        
        result['industry_id'] = TranslatorSFAccount.convertIndustry(SF_Account['Industry'],odoo)
        if SF_Account['Area_of_expertise__c']:
            result['expertise_area_ids'] = [(6, 0, TranslatorSFAccount.convertArea(SF_Account['Area_of_expertise__c'],odoo))]
        result['project_supplier_type_id'] = TranslatorSFAccount.convertProject(SF_Account['Supplier_Project__c'],odoo)
        if SF_Account['Activity__c']:
            result['client_activity_ids'] = [(6, 0, TranslatorSFAccount.convertActivity(SF_Account['Activity__c'],odoo))]
        if SF_Account['Product_Type__c']:
            result['client_product_ids'] = [(6, 0, TranslatorSFAccount.convertProduct(SF_Account['Product_Type__c'],odoo))]
        result['category_id'] =  [(6, 0, TranslatorSFAccount.convertCategory(SF_Account,odoo))]
        result['message_ids'] = [(0, 0, TranslatorSFAccount.generateLog(SF_Account))]

        return result
    
    @staticmethod
    def generateLog(SF_Account):
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
        result['Name'] = TranslatorSFAccount.test(Odoo_Contact.name)
        print(result['Name'])

        #result['Supplier_Status__c'] = TranslatorSFAccount.revertStatus(Odoo_Contact.stage)

        '''
        if SF_Account['BillingAddress']:
            result['city'] = SF_Account['BillingAddress']['city']
            result['zip'] = SF_Account['BillingAddress']['postalCode']
            result['street'] = SF_Account['BillingAddress']['street']
        '''

        result['Phone'] = Odoo_Contact.phone
        result['Fax'] = Odoo_Contact.fax
        # result['Sharepoint_Folder__c'] = TranslatorSFAccount.revertUrl(Odoo_Contact.sharepoint_folder)
        # Ignore description
        result['Website'] = Odoo_Contact.website

        # Ignore company_type
        result['BillingCountry'] = TranslatorSFAccount.revertCountry(Odoo_Contact.country_id.id, odoo)
        # result['user_id'] = TranslatorSFAccount.convertSfIdToOdooId(SF_Account['OwnerId'],odoo, SF)
        return result

    @staticmethod
    def convertStatus(SF):
        status = SF['Supplier_Status__c']
        if (status == 'Active - contract set up, information completed') or SF['Project_Controller__c']:
            return 3
        elif status == 'Prospective: no contract, pre-identify':
            return 2
        elif status == 'Inactive - reason mentioned':
            return 5
        elif SF['Is_supplier__c'] or SF['Supplier__c']: # New
            return 2
        else: # Undefined
            return 1
    
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
        mail = TranslatorSFAccount.getUserMail(ownerId,SF)
        return TranslatorSFAccount.getUserId(mail,odoo)
    
    @staticmethod
    def convertCategory(SFAccount, odoo):
        result = []
        SFtype = SFAccount['Type']
        if SFAccount['Is_supplier__c'] or SFAccount['Supplier__c']:
            result += [odoo.env.ref('vcls-contact.category_PS').id]
        elif SFAccount['Project_Controller__c'] and SFAccount['VCLS_Alt_Name__c']:
            result += [odoo.env.ref('vcls-contact.category_account').id]
        if SFtype:
            if (not SFAccount['Is_supplier__c'] or not SFAccount['Supplier__c']) and 'supplier' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_PS').id]
            if 'competitor' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_competitor').id]
            if 'partner' in SFtype.lower():
                result += [odoo.env.ref('vcls-contact.category_partner').id]
        return result
    
    @staticmethod
    def getUserMail(userId, SF):
        for user in TranslatorSFAccount.usersSF:
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
    def convertIndustry(SfIndustry,odoo):
        if SfIndustry:
            if 'pharma' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','Pharma')])
                if industry:
                    return industry[0].id

            elif 'biotechnology - therapeutics' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','Biotech')])
                if industry:
                    return industry[0].id

            elif 'medtech' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','Traditional MedTech')])
                if industry:
                    return industry[0].id

            elif 'biotech' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','Biotech')])
                if industry:
                    return industry[0].id

            elif 'consulting' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','Unknown')])
                if industry:
                    return industry[0].id

            elif 'biotechnology / r&d services' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','Biotech')])
                if industry:
                    return industry[0].id

            elif'cro' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','CRO')])
                if industry:
                    return industry[0].id

            elif 'healthcare' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','Unknown')])
                if industry:
                    return industry[0].id

            elif 'other' in SfIndustry.lower():
                industry = odoo.env['res.partner.industry'].search([('name','=','Unknown')])
                if industry:
                    return industry[0].id

            else:
                industry = odoo.env['res.partner.industry'].search([('name','=','Unknown')])
                if industry:
                    return industry[0].id

            """if 'pharma' in SfIndustry.lower():
                return odoo.env.ref('__export__.res_partner_industry_34_88c49c6e').id
            elif 'biotechnology - therapeutics' in SfIndustry.lower():
                return odoo.env.ref('__export__.res_partner_industry_35_05ac8f62').id
            elif 'medtech' in SfIndustry.lower():
                return odoo.env.ref('__export__.res_partner_industry_36_3bbdda7e').id
            elif 'biotech' in SfIndustry.lower():
                return odoo.env.ref('__export__.res_partner_industry_35_05ac8f62').id
            elif 'consulting' in SfIndustry.lower():
                return odoo.env.ref('vcls-contact.client_cat_health_product').id
            elif 'biotechnology / r&d services' in SfIndustry.lower():
                return odoo.env.ref('__export__.res_partner_industry_35_05ac8f62').id
            elif'cro' in SfIndustry.lower():
                return odoo.env.ref('__export__.res_partner_industry_42_704b94e6').id
            elif 'healthcare' in SfIndustry.lower():
                return odoo.env.ref('__export__.res_partner_industry_38_3c31212a').id
            elif 'other' in SfIndustry.lower():
                return odoo.env.ref('__export__.res_partner_industry_38_3c31212a').id
            else:
                return odoo.env.ref('__export__.res_partner_industry_44_858f790a').id"""
        return None
    
    @staticmethod
    def convertArea(SFArea,odoo):
        result = []
        if SFArea:
            if 'clinical development' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_c_dev').id]
            if 'regulatory company' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_reg_company').id]
            if 'medical Writer' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_mw').id]
            if 'non clinical development' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_nc_dev').id]
            if 'regulatory generalist' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_reg_generalist').id]
            if 'ohp' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_ohp').id]
            if 'atmp' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_atmp').id]
            if 'market access' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_ma').id]
            if '(bio) statistician' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_biostat').id]
            if 'database' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_db').id]
            if 'database management' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_db_mgmt').id]
            if 'cra' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_cra').id]
            if 'cro' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_cro').id]
            if 'pv' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_pv').id]
            if 'cmc' in SFArea.lower():
                result += [odoo.env.ref('vcls-suppliers.expertise_area_cmc').id]
        return result

    @staticmethod
    def convertActivity(SfActivity,odoo):
        result=[]
        if SfActivity:
            if 'develop/market healthcare products' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_cat_health_product').id]
            if 'service provider' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_cat_service_provider').id]
            if 'other type of third party' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_cat_other').id]
            if 'network, association, lobby' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_cat_network').id]
            if 'investor' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_cat_investor').id]
        return result
    @staticmethod
    def convertProduct(SfActivity,odoo):
        result=[]
        if SfActivity:
            if 'chemical drugs' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_prod_chem_drugs').id]
            if 'biologic drugs' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_prod_biol_drugs').id]
            if 'devices' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_prod_digital_device').id]
            if 'nutritionals and nutriceuticals' in SfActivity.lower():
                 result += [odoo.env.ref('vcls-contact.client_prod_nutri').id]
            if 'cell, gene & tissue therapy' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_prod_gene').id]
            if 'e-health' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_prod_ehealth').id]
            if 'other' in SfActivity.lower():
                result += [odoo.env.ref('vcls-contact.client_prod_other').id]
        return result
    
    @staticmethod
    def convertProject(SfProject,odoo):
        if SfProject:
            if 'freelance consultant' in SfProject.lower():
                return odoo.env.ref('vcls-suppliers.supplier_type_freelance').id
            elif 'kol' in SfProject.lower():
                return odoo.env.ref('vcls-suppliers.supplier_type_kol').id
            elif 'rrg associates' in SfProject.lower():
                return odoo.env.ref('vcls-suppliers.supplier_type_rrg').id
            elif 'consulting company' in SfProject.lower():
                return odoo.env.ref('vcls-suppliers.supplier_type_company').id
            elif 'translator' in SfProject.lower():
                return odoo.env.ref('vcls-suppliers.supplier_type_translator').id
        else:
            return None
    @staticmethod
    def convertCurrency(SfCurrency,odoo):
        odooCurr = odoo.env['res.currency'].search([('name','=',SfCurrency)]).id
        if odooCurr:
            return odooCurr
        else:
            return None