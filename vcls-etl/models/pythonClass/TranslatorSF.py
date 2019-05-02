from ITranslator import ITranslator

class TranslatorSF(ITranslator):
    @staticmethod
    def translateToOdoo(SF_Account):
        result = {}
        result['name'] = SF_Account['Name']
        # result['category_id'] = reference Supplier_Category__c
        result['stage'] = TranslatorSF.convertStatus(SF_Account['Supplier_Status__c'])
        # Ignore  Account_Level__c
        # result['country_id'] = reference  BillingCountry
        # result['state_id'] = reference  BillingState
        result['city'] = SF_Account['BillingAddress']['city']
        result['zip'] = SF_Account['BillingAddress']['postalCode']
        result['street'] = SF_Account['BillingAddress']['street']
        result['phone'] = SF_Account['Phone']
        # Ignore Area_of_expertise__c
        result['sharepoint_folder'] = TranslatorSF.convertUrl(SF_Account['Sharepoint_Folder__c']) # /!\
        result['description'] = SF_Account['Supplier_Description__c']
        result['description'] += '\n{}'.format(SF_Account['Key_Information__c'])
        # Ignore Supplier_Selection_Form_completed__c
        result['website'] = SF_Account['Website']
        return result
    @staticmethod
    def translateToSF(Odoo_Account):
        """ inverse method waiting for implementation """
        pass
    @staticmethod
    def convertStatus(status):
        if status == 'Active - contract set up, information completed':
            return 5
        elif status == 'Prospective: no contract, pre-identify':
            return 2
        elif status == 'Inactive - reason mentioned':
            return 4
        else: # Undefined
            return 1
    @staticmethod
    def convertUrl(url):
        if url == "No link for this relationship":
            return None
        startIndex = url.find('http://')
        endIndex = url.find('target')-2
        return url[startIndex:endIndex]