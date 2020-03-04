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
        KimbleOne__DeliveryStage__c,

        FROM KimbleOne__DeliveryGroup__c

"""

SELECT_GET_PROPOSAL_DATA = """

"""

STORE_TEMP = """
SELECT  ,, , ,  , , , ,   FROM  where Automated_Migration__c = TRUE
"""