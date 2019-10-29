from . import TranslatorSFGeneral
import logging
_logger = logging.getLogger(__name__)

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
        

        #New Therapeutic_Area Line Convertor
        if SF_Opportunity['Therapeutic_Area__c']:
            result['therapeutic_area_ids'] = [(6, 0,mapOdoo.convertRef(SF_Opportunity['Therapeutic_Area__c'], odoo, 'therapeutic.area', True))]

        if SF_Opportunity['VCLS_Activities__c']:
            result['client_activity_ids'] = [(6, 0,mapOdoo.convertRef(SF_Opportunity['VCLS_Activities__c'],odoo,'client.product',True))]

        result['date_deadline'] = SF_Opportunity['Deadline_for_Sending_Proposal__c'] 
        """ if SF_Opportunity['LeadSource']:
            print(SF_Opportunity['LeadSource'])
            result['source_id'] = mapOdoo.convertRef(SF_Opportunity['LeadSource'],odoo,'utm.source',False) """
        
        result['date_closed'] = SF_Opportunity['CloseDate']
        
        result['type'] = 'opportunity'
        
        if(SF_Opportunity['StageName']):
            result = TranslatorSFOpportunity.convertStageName(SF_Opportunity['StageName'],odoo,mapOdoo,result)
        
        if not 'probability' in result:
            result['probability'] = SF_Opportunity['Probability']
        #need test
        
        result['amount_customer_currency'] = SF_Opportunity['Amount']
        
        result['customer_currency_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Opportunity['CurrencyIsoCode'],odoo)
        
        if SF_Opportunity['Project_start_date__c']:
            result['expected_start_date'] = SF_Opportunity['Project_start_date__c']

        result.update(odoo.env['crm.lead']._onchange_partner_id_values(int(result['partner_id']) if result['partner_id'] else False))
        
        result['message_ids'] = [(0, 0, TranslatorSFOpportunity.generateLog(SF_Opportunity))]

        #_logger.info("TRANSLATOR OPPORTUNITY {}".format(result))

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
    def convertStageName(StageName,odoo,mapOdoo,result):
        if StageName == 'Closed Won':
            result['won_status'] = 'won'
            result['probability'] = 100
            stage_id = odoo.env['crm.stage'].search([('name','=','Closed Won')]).id
            if stage_id:
                result['stage_id'] = stage_id
        elif StageName == 'Closed Lost':
            result['won_status'] = 'lost'
            result['probability'] = 0
            result['active'] = False
        else:
            result['won_status'] = 'pending'
            result['stage_id'] = mapOdoo.convertRef(StageName,odoo,'crm.stage',False)

        return result



    