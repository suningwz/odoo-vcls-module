from odoo import models, fields, api
from . import ITranslator

class mapOdoo(models.Model):
    _name = 'map.odoo'
    _description = 'used to map external values to Odoo Ids'

    odModelName = fields.Char()
    externalName = fields.Char()
    externalOdooId = fields.Char()
    odooId = fields.Char()
    stage = fields.Selection([
        (1, 'New'),
        (2, 'Verified')],
        string='Stage',
        track_visibility='onchange',
        default=1,
    )
    
    @api.model
    def convertRef(self,SF,odoo,model,forMany): # convertRef
        results = []
        to_find = SF.split(';')
        for item in to_find:
            found = self.search([('externalName','=ilike',item),('odModelName','=',model)],limit=1)
            if found: #a map exist
                results.append(int(found.odooId))
            else: #we create a new map
                new_map = self.env[model].search([('name','ilike',item)],limit=1)
                if new_map:
                    results.append(new_map.id)
                    self.create({
                        'adModelName':model,
                        'externalName':item.lower(),
                        'odooId':str(new_map.id),
                        'stage':1,
                    })
                else:
                    self.create({
                        'adModelName':model,
                        'externalName':item.lower(),
                        'stage':1,
                    })

        if forMany:
            return results
        elif results:
            return results[0]
        else:
            return []



    """
        element = []
        SF = SF.split(';')
        for sfname in SF:
            try:
                element = self.getRef(sfname.lower(),odoo,model)
            except ITranslator.KeyNotFoundError:
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

    @api.model
    def getRef(self,SFName,odoo,model): # getRef
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
        raise ITranslator.KeyNotFoundError"""