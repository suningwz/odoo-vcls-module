from . import TranslatorSFGeneral

class TranslatorSFContract(TranslatorSFGeneral.TranslatorSFGeneral):
    def __init__(self,SF):
        super().__init__(SF)

    @staticmethod
    def translateToOdoo(SF_Contract, odoo, SF):
        mapOdoo = odoo.env['map.odoo']
        result = {}
        # Modify the name with -test
        result['code'] = SF_Contract['ContractNumber']
        if SF_Contract['Name']:
            result['internal_name'] = SF_Contract['Name'] #+ '-test'
        else:
            result['internal_name'] = "the only one contract without name"
        if SF_Contract['External_Contract_Name__c']:
            result['name'] = SF_Contract['External_Contract_Name__c']
        else:
            result['name'] = result['internal_name']

        if SF_Contract['Type_of_Contract__c']:    
            result['agreement_type_id'] = mapOdoo.convertRef(SF_Contract['Type_of_Contract__c'], odoo, 'agreement.type', False)
        
        if SF_Contract['VCLS_Status__c']:
            result['stage_id'] = mapOdoo.convertRef(SF_Contract['VCLS_Status__c'], odoo, 'agreement.stage', False)

        if SF_Contract['Link_to_Parent_Contract__c']:
            result['parent_agreement_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Contract['Link_to_Parent_Contract__c'],'agreement','Contract',odoo)
        
        if SF_Contract['CompanySignedDate']:
            result['company_signed_date'] = SF_Contract['CompanySignedDate']

        if SF_Contract['CompanySignedId']:
            result['company_signed_user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUserId(SF_Contract['CompanySignedId'],odoo, SF)
        
        if SF_Contract['CustomerSignedId']:
            result['partner_signed_user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Contract['CustomerSignedId'],'res.partner','Contact', odoo)

        if SF_Contract['CustomerSignedDate']:
            result['partner_signed_date'] = SF_Contract['CustomerSignedDate']

        if SF_Contract['Contract_URL__c']:
            result['contract_url'] = SF_Contract['Contract_URL__c']
        
        if SF_Contract['OwnerId']:
            result['assigned_user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUserId(SF_Contract['OwnerId'],odoo, SF)

        if SF_Contract['AccountId']:
            result['partner_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Contract['AccountId'],'res.partner','Account',odoo)
        
        if SF_Contract['Contract_End_Date__c']:
            result['end_date'] = SF_Contract['Contract_End_Date__c']

        result['company_id'] = False
        
        return result

    @staticmethod
    def translateToSF(Odoo_Contact, odoo):
        pass
    """    result = {}
        # Modify the name with -test
        if ' ' in Odoo_Contact.name:
            name = Odoo_Contact.name.split(" ")
            if len(name) > 2:
                result['LastName'] = Odoo_Contact.name
            else:
                result['FirstName'], result['LastName'] = name
        else:
            result['LastName'] = Odoo_Contact.name
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
            
        result['AccountId'] = TranslatorSFGeneral.TranslatorSFGeneral.toSfId(Odoo_Contact.parent_id.id,"res.partner", "Account",odoo)
        
        # Ignore company_type
        result['MailingCountry'] = TranslatorSFGeneral.TranslatorSFGeneral.revertCountry(Odoo_Contact.country_id.id, odoo)
        result['CurrencyIsoCode'] = Odoo_Contact.currency_id.name
        if Odoo_Contact.user_id:
            result['OwnerId'] = TranslatorSFGeneral.TranslatorSFGeneral.revertOdooIdToSfId(Odoo_Contact.user_id,odoo)
        elif Odoo_Contact.parent_id:
            result['OwnerId'] = TranslatorSFGeneral.TranslatorSFGeneral.revertOdooIdToSfId(Odoo_Contact.parent_id.user_id,odoo)
        for c in Odoo_Contact.category_id:
            category += c.name 
        result['Category__c'] = category
        result['Salutation'] = Odoo_Contact.title.name
        result['Title'] = Odoo_Contact.function


        return result """