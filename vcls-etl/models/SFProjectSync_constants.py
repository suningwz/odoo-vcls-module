# -*- coding: utf-8 -*-

###############################
# QUERIES #
###############################

SELECT_GET_ELEMENT_DATA = """
    SELECT
        Id,
        Name,
        KimbleOne__DeliveryGroup__c,
        KimbleOne__OriginatingProposal__c,
        Activity__c,
        KimbleOne__Product__c,
        Contracted_Budget__c,
        KimbleOne__InvoicingCurrencyContractRevenue__c

        FROM KimbleOne__DeliveryElement__c

"""

SELECT_GET_PROJECT_DATA = """
    SELECT
        Id,
        Name,
        KimbleOne__Reference__c,
        KimbleOne__Account__c,
        KimbleOne__Proposal__c,
        
        KimbleOne__InvoicingCurrencyIsoCode__c,
        Scope_of_Work_Description__c,
        Activity__c,
        KimbleOne__ExpectedEndDate__c,
        KimbleOne__ForecastStatus__c,
        KimbleOne__DeliveryStage__c

        FROM KimbleOne__DeliveryGroup__c

"""

SELECT_GET_PROPOSAL_DATA = """
    SELECT 
        Id, 
        KimbleOne__Opportunity__c, 
        KimbleOne__DeliveryStartDate__c, 
        KimbleOne__BusinessUnit__c 

        FROM KimbleOne__Proposal__c
"""

SELECT_GET_MILESTONE_DATA = """
    SELECT 
        Id,
        Name,
        KimbleOne__DeliveryElement__c,
        KimbleOne__InvoicingCurrencyMilestoneValue__c,
        KimbleOne__InvoiceItemStatus__c,
        KimbleOne__MilestoneDate__c,
        KimbleOne__MilestoneStatus__c,
        KimbleOne__MilestoneType__c
        
        FROM KimbleOne__Milestone__c
"""



STORE_TEMP = """

SELECT Id, KimbleOne__DeliveryGroup__c,KimbleOne__ActivityRole__c,KimbleOne__InvoicingCurrencyRevenueRate__c  FROM KimbleOne__ActivityAssignment__c
WHERE KimbleOne__ActivityRole__c  != NULL AND KimbleOne__DeliveryGroup__c != NULL


"""