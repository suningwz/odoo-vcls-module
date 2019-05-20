from odoo import models, fields, api
from . import ITranslator

class mapOdoo(models.Model):
    _name = 'map.odoo'
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
        raise ITranslator.KeyNotFoundError