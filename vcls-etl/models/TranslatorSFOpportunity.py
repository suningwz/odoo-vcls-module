from . import ITranslator

class KeyNotFoundError(Exception):
    pass

class TranslatorSFOpportunity(ITranslator.ITranslator):

    def __init__(self,SF):
        queryUser = "Select Username,Id FROM User"
        TranslatorSFOpportunity.usersSF = SF.query(queryUser)['records']
    
    @staticmethod
    def translateToOdoo(SF_Opportunity, odoo, SF):
        result = {}
        result['name'] = SF_Opportunity['Name']
        #ignore stage
        result['partner_id'] = TranslatorSFOpportunity.toOdooId(SF_Opportunity['AccountId'],odoo)
        result['user_id'] = TranslatorSFOpportunity.convertSfIdToOdooId(SF_Opportunity['OwnerId'],odoo,SF)
        result['expected_revenue'] = SF_Opportunity['ExpectedRevenue']
        if SF_Opportunity['Reasons_Lost_Comments__c']:
            result['lost_reason'] = TranslatorSFOpportunity.convertId(SF_Opportunity['Reasons_Lost_Comments__c'],odoo,'crm.lost.reason',False)
        result['probability'] = SF_Opportunity['Probability']
        result['description'] = ''
        if SF_Opportunity['Description']:
            result['description'] +='Description : ' + str(SF_Opportunity['Description']) + '\n'
        if SF_Opportunity['Client_Product_Description__c']:
            result['description'] +='Client Product Description : ' +  str(SF_Opportunity['Client_Product_Description__c'])
        result['company_currency'] = TranslatorSFOpportunity.convertCurrency(SF_Opportunity['CurrencyIsoCode'],odoo)
        if SF_Opportunity['Product_Category__c']:
            result['client_product_ids'] =[(6, 0, TranslatorSFOpportunity.convertId(SF_Opportunity['Product_Category__c'],odoo,'client.product',True))]
        if SF_Opportunity['Geographic_Area__c']:
            result['country_group_id'] = TranslatorSFOpportunity.convertId(SF_Opportunity['Geographic_Area__c'],odoo,'res.country.group',False)
        if SF_Opportunity['VCLS_Activities__c']:
            result['client_activity_ids'] = [(6, 0,TranslatorSFOpportunity.convertId(SF_Opportunity['VCLS_Activities__c'],odoo,'client.product',True))]
        result['date_deadline'] = SF_Opportunity['Deadline_for_Sending_Proposal__c'] 
        result['source_id'] = TranslatorSFOpportunity.convertId(SF_Opportunity['LeadSource'],odoo,'utm.source',False)
        result['date_closed'] = SF_Opportunity['CloseDate']
        result.update(odoo.env['crm.lead']._onchange_partner_id_values(int(result['partner_id']) if result['partner_id'] else False))
        result['message_ids'] = [(0, 0, TranslatorSFOpportunity.generateLog(SF_Opportunity))]
        return result
    
    @staticmethod
    def generateLog(SF_Opportunity):
        result = {
            'model': 'crm.lead',
            'message_type': 'comment',
            'body': '<p>Updated.</p>'
        }

        return result
    @staticmethod
    def translateToSF(Odoo_Account):
        pass
    @staticmethod
    def convertSfIdToOdooId(ownerId, odoo, SF):
        mail = TranslatorSFOpportunity.getUserMail(ownerId,SF)
        return TranslatorSFOpportunity.getUserId(mail,odoo)
    
    @staticmethod
    def getUserMail(userId, SF):
        for user in TranslatorSFOpportunity.usersSF:
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
        for user in TranslatorSFOpportunity.usersSF:
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