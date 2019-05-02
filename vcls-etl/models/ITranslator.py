from abc import ABC, abstractmethod

class ITranslator(ABC):
    
    @staticmethod
    @abstractmethod
    def translateToOdoo(SF_Account):
        pass
    
    @staticmethod
    @abstractmethod
    def translateToSF(Odoo_Account):
        pass