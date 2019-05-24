from . import ITranslator

class TranslatorOutlookContact(ITranslator.ITranslator):

    @staticmethod
    def translateToOdoo(Contact, odoo, SF):
        mapOdoo = odoo.env['map.odoo']
        result = {}
        if Contact['Title']:
            result['title'] = mapOdoo.convertRef(Contact['Title'], odoo,'res.partner.title',False)
        result['name'] = Contact['First Name'] + Contact['Last Name']
        #Contact['Sufix']
        #result['parent_id'] = Contact['Company"]
        #Contcat['Department'] Paris OR RENNES
        result['function'] = Contact['Job Title']
        result['street'] = Contact['Business Street']
        result['city'] = Contact['Business City']
        result['state'] = Contact['Business State']
        result['zip'] = Contact['Business Postal Code']
        if Contact['Business Country/Region']:
            result['country_id'] = mapOdoo.convertRef(Contact['Business Country/Region'],odoo,'res.country',False)
        ''' result['description'] = 'Home Address : ' + Contact['Home Street'] 
        + Contact['Home City'] + Contact['Home State'] + Contact['Home Postal Code']
        + Contact['Home Country']
        result['description'] += 'Other Address : ' + Contact['Other Street'] + Contact['Other City'] +Contact['Other Country/Region']
        result['fax'] = Contact['Business Fax']
        result['phone'] = Contact['Business Phone'] 
        Contact['Business Phone2']
        Contact['Home Phone']
        Contact['Home Phone2']
        Contact['Mobile Phone']
        Contact['Other Fax']
        Contact['Other Phone']
        Contact['Pager']
        Contact['Categories']'''
        result['email'] = Contact['E-mail Address']
        '''
        Contact['E-mail 2 Address']
        Contact['E-mail 3 Address']
        Contact['Initials']
        Contact["Manager's Name"]'''
        Contact['description'] += Contact['Notes']
        result['website'] = Contact['Web Page']

        return result

    @staticmethod
    def translateToSF(Odoo_Account):
        pass