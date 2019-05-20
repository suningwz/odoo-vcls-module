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
    def translateToSF(Odoo_Account):
        pass

    @staticmethod
    def convertId(SF,odoo,model,forMany): # convertRef
        element = []
        SF = SF.split(';')
        for sfname in SF:
            try:
                element = ITranslator.toOD_id(sfname.lower(),odoo,model)
            except KeyNotFoundError:
                odooRef = odoo.env[model].search([('name','ilike',sfname)],limit=1)
                if odooRef:
                    element.append(odooRef.id)
                    odoo.env['map.odoo'].create({'odModelName':model, 'externalName' : sfname.lower(), 'odooId':odooRef.id, 'stage':1})
                else:
                    odoo.env['map.odoo'].create({'odModelName':model, 'externalName' : sfname.lower(), 'stage':1})
                # add toReviewed for maintain the mapping via UI ODOO

        if not element:
            return []

        if forMany:
            return element
        return element[0]

    @staticmethod
    def toOD_id(SFName,odoo,model): # getRef
        result = []
        mapping = odoo.env['map.odoo'].search([('externalName','=ilike',SFName),('odModelName','=',model)])
        if mapping:
            for m in mapping:
                if m.odooId:
                    result.append(m.odooId)
                elif m.externalOdooId:
                    result.append(odoo.env.ref(m.externalOdooId).id) 
            return result

        #There is no mapping object for this SFName    
        raise KeyNotFoundError