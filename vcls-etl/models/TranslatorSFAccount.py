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
        
        if SF_Account['BillingCountry']:
            result['country_id'] = TranslatorSFAccount.convertId(SF_Account['BillingCountry'],odoo,'res.country',False)
        
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
        result['currency_id'] = TranslatorSFAccount.convertCurrency(SF_Account['CurrencyIsoCode'],odoo)
        result['altname'] = SF_Account['VCLS_Alt_Name__c']
        result['user_id'] = TranslatorSFAccount.convertUserId(SF_Account['OwnerId'],odoo, SF)

        if SF_Account['Invoice_Administrator__c']:
           result['invoice_admin_id'] = TranslatorSFAccount.convertId(SF_Account['Invoice_Administrator__c'],odoo,'res.users',False)
        if SF_Account['Main_VCLS_Contact__c']:
            result['expert_id'] = TranslatorSFAccount.convertUserId(SF_Account['Main_VCLS_Contact__c'],odoo, SF)
        if SF_Account['Project_Assistant__c']:
            result['assistant_id'] = TranslatorSFAccount.convertUserId(SF_Account['Project_Assistant__c'],odoo, SF)
        if SF_Account['Project_Controller__c']:
            result['controller_id'] = TranslatorSFAccount.convertUserId(SF_Account['Project_Controller__c'],odoo, SF)
        if SF_Account['Industry']:
            result['industry_id'] = TranslatorSFAccount.convertId(SF_Account['Industry'],odoo,'res.partner.industry',False)
        if SF_Account['Area_of_expertise__c']:
            result['expertise_area_ids'] = [(6, 0, TranslatorSFAccount.convertId(SF_Account['Area_of_expertise__c'],odoo,'expertise.area',True))]
        if SF_Account['Supplier_Project__c']:
            result['project_supplier_type_id'] = TranslatorSFAccount.convertId(SF_Account['Supplier_Project__c'],odoo,'project.supplier.type',False)
        if SF_Account['Activity__c']:
            result['client_activity_ids'] = [(6, 0, TranslatorSFAccount.convertId(SF_Account['Activity__c'],odoo,'client.activity',True))]
        if SF_Account['Product_Type__c']:
            result['client_product_ids'] = [(6, 0, TranslatorSFAccount.convertId(SF_Account['Product_Type__c'],odoo,'client.product',True))]
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
    def translateToSF(Odoo_Contact, odoo):
        result = {}
        # Modify the name with -test
        result['Name'] = Odoo_Contact.name
        print(result['Name'])

        #result['Supplier_Status__c'] = TranslatorSFAccount.revertStatus(Odoo_Contact.stage)
        result['BillingAddress'] = {}
        result['BillingAddress']['city'] = Odoo_Contact.city
        result['BillingAddress']['postalCode'] = Odoo_Contact.zip
        result['BillingAddress']['street'] = Odoo_Contact.street
        result['Phone'] = Odoo_Contact.phone
        result['Fax'] = Odoo_Contact.fax
        # result['Sharepoint_Folder__c'] = TranslatorSFAccount.revertUrl(Odoo_Contact.sharepoint_folder)
        # Ignore description
        result['Website'] = Odoo_Contact.website

        # Ignore company_type
        result['BillingCountry'] = TranslatorSFAccount.revertCountry(Odoo_Contact.country_id.id, odoo)
        # result['user_id'] = TranslatorSFAccount.convertUserId(SF_Account['OwnerId'],odoo, SF)
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
    def revertCountry(country, odoo):
        if country:
            return odoo.env['res.country'].browse(country).name
        return None

    @staticmethod
    def convertUserId(ownerId, odoo, SF):
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
    def getUserIdSf(mail):
        for user in TranslatorSFAccount.usersSF:
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
    def convertCurrency(SfCurrency,odoo):
        odooCurr = odoo.env['res.currency'].search([('name','=',SfCurrency)]).id
        if odooCurr:
            return odooCurr
        else:
            return None
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