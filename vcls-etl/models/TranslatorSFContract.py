from . import TranslatorSFGeneral

import logging
_logger = logging.getLogger(__name__)

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

        result = TranslatorSFContract.type_and_subtype(result,SF_Contract,odoo,mapOdoo)
        
        if SF_Contract['VCLS_Status__c']:
            _logger.info("ETL | Contract Stage {}".format(SF_Contract['VCLS_Status__c']))
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
        
        result['expiration_notice'] = SF_Contract['OwnerExpirationNotice']
        result['start_date'] = SF_Contract['StartDate']
        result['special_terms'] = SF_Contract['SpecialTerms']
        result['description'] = SF_Contract['Description']
        result['approved_date'] = SF_Contract['LastApprovedDate']
        #result['parent_agreement_name'] = SF_Contract['Parent_Contract_Name__c']
        #result['parent_agreement_type'] = SF_Contract['Parent_Contract_Type__c']
        return result

    @staticmethod
    def translateToSF(Odoo_Contract, odoo):
        pass

    @staticmethod
    def type_and_subtype(result,SF, odoo, mapOdoo):
        if SF['Type_of_Contract__c']:

            type_id = mapOdoo.convertRef(SF['Type_of_Contract__c'], odoo, 'agreement.type', False)  
            result['agreement_type_id'] = type_id
            if type_id:
                _logger.info("Type ID {}".format(type_id))
                has_sub = odoo.env['agreement.subtype'].search([('agreement_type_id','=',type_id)])
                if has_sub:
                    result['agreement_subtype_id'] = mapOdoo.convertRef(SF['Type_of_Contract__c'], odoo, 'agreement.subtype', False)
                else:
                    pass
            else:
                pass
        else:
            pass
        
        return result
        