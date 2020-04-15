from abc import ABC, abstractmethod

class KeyNotFoundError(Exception):
    pass

class ITranslator(ABC):
    
    @staticmethod
    @abstractmethod
    def translateToOdoo(SF_Account):
        pass
    
    @staticmethod
    @abstractmethod
    def translateToAccess(Odoo_Account):
        pass

    @staticmethod
    def revertCountry(country, odoo):
        if country:
            return odoo.env['res.country'].browse(country).name
        return None
    