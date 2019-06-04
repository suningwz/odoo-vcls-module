from . import ITranslator

class TranslatorSFGeneral(ITranslator.ITranslator):
    def __init__(self,SF):
        queryUser = "Select Username,Id FROM User"
        TranslatorSFGeneral.usersSF = SF.query(queryUser)['records']
        
    @staticmethod
    def convertUrl(url):
        if url == "No link for this relationship":
            return None
        startIndex = url.find('http://')>0
        endIndex = url.find('target')-2
        return url[startIndex:endIndex]
    
    @staticmethod
    def revertUrl(url):
        if not url:
            return "No link for this relationship"
        else:
            return '<a href="{}" target="_blank">Supplier Folder</a>'.format(url)

    @staticmethod
    def convertUserId(ownerId, odoo, SF):
        mail = TranslatorSFGeneral.getUserMail(ownerId,SF)
        return TranslatorSFGeneral.getUserId(mail,odoo)
    @staticmethod
    def revertOdooIdToSfId(idodoo,odoo):
        mail = TranslatorSFGeneral.getUserMailOd(idodoo.id,odoo)
        return TranslatorSFGeneral.getUserIdSf(mail)

    @staticmethod
    def getUserMail(userId, SF):
        for user in TranslatorSFGeneral.usersSF: 
            if user['Id'] == userId:
                return user['Username']
        return None

    @staticmethod
    def getUserId(mail, odoo):
        result = odoo.env['res.users'].search([('email','=',mail)])
        if result:
            return result[0].id
        else:
            return None
    @staticmethod
    def getUserIdSf(mail):
        for user in TranslatorSFGeneral.usersSF:
            if user['Username'] == mail:
                return user['Id']
        return None
    @staticmethod
    def getUserMailOd(userId,odoo):
        result = odoo.env['res.users'].search([('id','=',userId)])
        if result:
            return result[0].email
        else:
            return None
    
    @staticmethod
    def convertCurrency(SfCurrency,odoo):
        odooCurr = odoo.env['res.currency'].search([('name','=',SfCurrency)]).id
        if odooCurr:
            return odooCurr
        else:
            return None
    @staticmethod
    def toOdooId(externalId, odooModelName, externalObjName, odoo):
        keyodooId = odoo.env['etl.sync.keys'].search([('odooModelName','=',odooModelName),('externalObjName','=',externalObjName),('externalId','=',str(externalId))])
        if keyodooId:
            return int(keyodooId.odooId)
        return None
    
    @staticmethod
    def toSfId(odooId, odooModelName, externalObjName, odoo):
        keyExtId = odoo.env['etl.sync.keys'].search([('odooModelName','=',odooModelName),('externalObjName','=',externalObjName),('odooId','=',str(odooId))])
        if keyExtId:
            return keyExtId.externalId
        return None
        
    @staticmethod
    def convertSfIdToOdooId(ownerId, odoo, SF):
        mail = TranslatorSFGeneral.getUserMail(ownerId,SF)
        return TranslatorSFGeneral.getUserId(mail,odoo)