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


"SELECT ,, ,  FROM KimbleOne__DeliveryElement__c WHERE KimbleOne__DeliveryGroup__c IN (SELECT Id  FROM KimbleOne__DeliveryGroup__c where Automated_Migration__c = TRUE)
"