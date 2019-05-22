from . import TranslatorSFGeneral

class KeyNotFoundError(Exception):
    pass

class TranslatorSFLeads(TranslatorSFGeneral.TranslatorSFGeneral):
    def __init__(self,SF):
        super().__init__(SF)
    
    @staticmethod
    def translateToOdoo(SF_Leads, odoo, SF):
        mapOdoo = odoo.env['map.odoo']
        result = {}
        result['name'] = SF_Leads['Name']
        #ignore stage
        result['partner_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Leads['AccountId'],odoo)
        result['user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertSfIdToOdooId(SF_Leads['OwnerId'],odoo,SF)
        result['expected_revenue'] = SF_Leads['ExpectedRevenue']
        if SF_Leads['Reasons_Lost_Comments__c']:
            result['lost_reason'] = mapOdoo.convertRef(SF_Leads['Reasons_Lost_Comments__c'],odoo,'crm.lost.reason',False)
        result['probability'] = SF_Leads['Probability']
        result['description'] = ''
        if SF_Leads['Description']:
            result['description'] +='Description : ' + str(SF_Leads['Description']) + '\n'
        if SF_Leads['Client_Product_Description__c']:
            result['description'] +='Client Product Description : ' +  str(SF_Leads['Client_Product_Description__c'])
        result['company_currency'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Leads['CurrencyIsoCode'],odoo)
        if SF_Leads['Product_Category__c']:
            result['client_product_ids'] =[(6, 0, mapOdoo.convertRef(SF_Leads['Product_Category__c'],odoo,'client.product',True))]
        if SF_Leads['Geographic_Area__c']:
            result['country_group_id'] = mapOdoo.convertRef(SF_Leads['Geographic_Area__c'],odoo,'res.country.group',False)
        if SF_Leads['VCLS_Activities__c']:
            result['client_activity_ids'] = [(6, 0,mapOdoo.convertRef(SF_Leads['VCLS_Activities__c'],odoo,'client.product',True))]
        result['date_deadline'] = SF_Leads['Deadline_for_Sending_Proposal__c'] 
        result['source_id'] = mapOdoo.convertRef(SF_Leads['LeadSource'],odoo,'utm.source',False)
        result['date_closed'] = SF_Leads['CloseDate']
        result['type'] = 'opportunity'
        #need test
        result['amount_customer_currency'] = SF_Leads['Amount'] #need try catch
        result['customer_currency_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Leads['CurrencyIsoCode'],odoo)#need try catch
        if SF_Leads['Project_start_date__c']:
            result['expected_start_date'] = SF_Leads['Project_start_date__c']

        result.update(odoo.env['crm.lead']._onchange_partner_id_values(int(result['partner_id']) if result['partner_id'] else False))
        result['message_ids'] = [(0, 0, TranslatorSFLeads.generateLog(SF_Leads))]


        return result
    
    @staticmethod
    def generateLog(SF_Leads):
        result = {
            'model': 'crm.lead',
            'message_type': 'comment',
            'body': '<p>Updated.</p>'
        }

        return result
    @staticmethod
    def translateToSF(Odoo_Account):
        pass
    