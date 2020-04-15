from . import TranslatorACGeneral
import logging
_logger = logging.getLogger(__name__)

class TranslatorACClient(TranslatorACGeneral.TranslatorACGeneral):
    def __init__(self,SF):
        super().__init__(SF)

    @staticmethod
    def translateToOdoo(AC_Client, odoo, AC):
        mapOdoo = odoo.env['map.odoo']
        
        result = {}
        
        ### IDENTIFICATION
        result['name'] = AC_Client['Name']

        _logger.info(result)
        return result

    
    @staticmethod
    def generateLog(SF_Campaign):
        result = {
            'model': 'res.partner',
            'message_type': 'comment',
            'body': '<p>Access Synchronization</p>'
        }

        return result


    @staticmethod
    def translatranslateToAccess(Odoo_Contact, odoo):
        pass
    
    
    

    