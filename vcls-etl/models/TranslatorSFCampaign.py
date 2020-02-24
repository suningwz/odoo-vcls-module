from . import TranslatorSFGeneral
import logging
_logger = logging.getLogger(__name__)

class TranslatorSFCampaign(TranslatorSFGeneral.TranslatorSFGeneral):
    def __init__(self,SF):
        super().__init__(SF)

    @staticmethod
    def translateToOdoo(SF_Campaign, odoo, SF):
        mapOdoo = odoo.env['map.odoo']
        
        result = {}
        
        ### IDENTIFICATION
        result['name'] = SF_Campaign['Name']
        
         ### RELATIONS
        if SF_Campaign['ParentId']:
            result['parent_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Campaign['ParentId'],"project.task","Campaign",odoo)
        if SF_Campaign['OwnerId']:
            result['user_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUserId(SF_Campaign['OwnerId'],odoo, SF)
        if not result['user_id']:
            result['user_id'] = 2
        if SF_Campaign['Conference_Organisation__c']:
            result['organizer_id'] = TranslatorSFGeneral.TranslatorSFGeneral.toOdooId(SF_Campaign['Conference_Organisation__c'],"res.partner","Account",odoo) 
        if SF_Campaign['CreatedById']:
            result['create_uid'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUserId(SF_Campaign['CreatedById'],odoo, SF)
        result['create_date'] = SF_Campaign['CreatedDate']
        if SF_Campaign['CurrencyIsoCode']:
            result['currency_id'] = TranslatorSFGeneral.TranslatorSFGeneral.convertCurrency(SF_Campaign['CurrencyIsoCode'],odoo)

        result['description'] = ''
        if SF_Campaign['Description']:
            result['description'] += 'Description:\n' + str(SF_Campaign['Description']) + '\n'
        if SF_Campaign['Name_of_presentation_given__c']:
            result['description'] += 'Name of presentation given:\n' + str(SF_Campaign['Name_of_presentation_given__c']) + '\n'
        if SF_Campaign['Purpose_of_attendance__c']:
            result['description'] += 'Purpose of attendance:\n' + str(SF_Campaign['Purpose_of_attendance__c']) + '\n'
        if SF_Campaign['Post_Event_Feedback__c']:
            result['description'] += 'Post Event Feedback\n' + str(SF_Campaign['Post_Event_Feedback__c'])

        result['date_end'] = SF_Campaign['EndDate']
        result['active'] = SF_Campaign['IsActive']
        if SF_Campaign['LastModifiedById']:
            result['write_uid'] = TranslatorSFGeneral.TranslatorSFGeneral.convertUserId(SF_Campaign['LastModifiedById'],odoo, SF)
        result['write_date'] = SF_Campaign['LastModifiedDate']

        if SF_Campaign['Name_of_attendee_1__c']:
            attendee1 = TranslatorSFGeneral.TranslatorSFGeneral.convertSfContactToOdooEmploye(SF_Campaign['Name_of_attendee_1__c'],odoo)
            if attendee1:
                result['attendee_ids'] = [(4, attendee1)]
        if SF_Campaign['Name_of_attendee_2__c']:
            attendee2 = TranslatorSFGeneral.TranslatorSFGeneral.convertSfContactToOdooEmploye(SF_Campaign['Name_of_attendee_2__c'],odoo)
            if attendee2:
                result['attendee_ids'] = [(4, attendee2)]
        if SF_Campaign['Name_of_attendee_1__c'] and SF_Campaign['Name_of_attendee_1__c']:
            attendee1 = TranslatorSFGeneral.TranslatorSFGeneral.convertSfContactToOdooEmploye(SF_Campaign['Name_of_attendee_1__c'],odoo)
            attendee1 = TranslatorSFGeneral.TranslatorSFGeneral.convertSfContactToOdooEmploye(SF_Campaign['Name_of_attendee_2__c'],odoo)
            if attendee1 and attendee2:
                attendee = [attendee1,attendee1]
                result['attendee_ids'] = [(6, 0, attendee)]


        result['contact_count'] = SF_Campaign['NumberOfContacts']
        result['lead_count'] = SF_Campaign['NumberOfLeads']
        result['opp_count'] = SF_Campaign['NumberOfOpportunities']     
        result['registration_cost'] = SF_Campaign['Registration_Costs__c']
        result['saved_cost'] = SF_Campaign['Savings_negotiated__c']
        result['sponsorship_cost'] = SF_Campaign['Sponsorship_costs__c']
        result['date_start'] = SF_Campaign['StartDate']
        
        if SF_Campaign['Status']:
            stage = mapOdoo.convertRef(SF_Campaign['Status'],odoo,'project.task.type',False)
            if stage:
                result['stage_id'] = int(stage)
            

        result['total_cost'] = SF_Campaign['Total_Cost__c']
        result['travel_cost'] = SF_Campaign['Travel_cost__c']
        
        if SF_Campaign['Type']:
            project_id = mapOdoo.convertRef(SF_Campaign['Type'],odoo,'project.project',False)
            if project_id:
                result['project_id'] = int(project_id)

        #SF_Campaign['LastReferencedDate']
        #SF_Campaign['LastViewedDate']
        #SF_Campaign['NumberOfConvertedLeads']
        #SF_Campaign['Number_of_delegates__c']
        #SF_Campaign['Region__c']
        #SF_Campaign['Business_Unit__c']

        _logger.info(result)
        return result

    
    @staticmethod
    def generateLog(SF_Campaign):
        result = {
            'model': 'project.task',
            'message_type': 'comment',
            'body': '<p>Salesforce Synchronization</p>'
        }

        return result


    @staticmethod
    def translateToSF(Odoo_Contact, odoo):
        pass
    
    
    

    