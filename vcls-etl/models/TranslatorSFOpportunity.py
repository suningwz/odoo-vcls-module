from . import TranslatorSFGeneral

class KeyNotFoundError(Exception):
    pass

class TranslatorSFOpportunity(TranslatorSFGeneral.TranslatorSFGeneral):
    def __init__(self,SF):
        super().__init__(SF)
    
    @staticmethod
    def translateToOdoo(SF_Opportunity, odoo, SF):
        mapOdoo = odoo.env['map.odoo']
        result = {}
        result['name'] = SF_Opportunity['Name']
        #ignore stage
        result['partner_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Opportunity['AccountId'],"res.partner","Account",odoo)
        result['user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertSfIdToOdooId(SF_Opportunity['OwnerId'],odoo,SF)
        result['expected_revenue'] = SF_Opportunity['ExpectedRevenue']
        result['type'] = 'opportunity'
        if SF_Opportunity['Reasons_Lost_Comments__c']:
            result['lost_reason'] = mapOdoo.convertRef(SF_Opportunity['Reasons_Lost_Comments__c'],odoo,'crm.lost.reason',False)
        result['probability'] = SF_Opportunity['Probability']
        result['description'] = ''
        if SF_Opportunity['Description']:
            result['description'] +='Description : ' + str(SF_Opportunity['Description']) + '\n'
        if SF_Opportunity['Client_Product_Description__c']:
            result['description'] +='Client Product Description : ' +  str(SF_Opportunity['Client_Product_Description__c'])
        result['customer_currency_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Opportunity['CurrencyIsoCode'],odoo)
        if SF_Opportunity['Product_Category__c']:
            result['client_product_ids'] =[(6, 0, mapOdoo.convertRef(SF_Opportunity['Product_Category__c'],odoo,'client.product',True))]
        if SF_Opportunity['Geographic_Area__c']:
            result['country_group_id'] = mapOdoo.convertRef(SF_Opportunity['Geographic_Area__c'],odoo,'res.country.group',False)
        if SF_Opportunity['VCLS_Activities__c']:
            result['client_activity_ids'] = [(6, 0,mapOdoo.convertRef(SF_Opportunity['VCLS_Activities__c'],odoo,'client.product',True))]
        result['date_deadline'] = SF_Opportunity['Deadline_for_Sending_Proposal__c'] 
        """ if SF_Opportunity['LeadSource']:
            print(SF_Opportunity['LeadSource'])
            result['source_id'] = mapOdoo.convertRef(SF_Opportunity['LeadSource'],odoo,'utm.source',False) """
        result['date_closed'] = SF_Opportunity['CloseDate']
        result['type'] = 'opportunity'
        #need test
        result['amount_customer_currency'] = SF_Opportunity['Amount'] #need try catch
        result['customer_currency_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Opportunity['CurrencyIsoCode'],odoo)#need try catch
        if SF_Opportunity['Project_start_date__c']:
            result['expected_start_date'] = SF_Opportunity['Project_start_date__c']

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
    