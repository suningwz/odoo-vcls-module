from . import ITranslator

class TranslatorACGeneral(ITranslator.ITranslator):
    def __init__(self,SF):
        pass

    @staticmethod
    def toOdooId(externalId, odooModelName, externalObjName, odoo):
        keyodooId = odoo.env['etl.sync.access.keys'].search([('odooModelName','=',odooModelName),('externalObjName','=',externalObjName),('externalId','=',str(externalId))])
        if keyodooId:
            return int(keyodooId.odooId)
        return None
        
    @staticmethod
    def convertCityId(CityID, access):
        row = access.execute('select City from tblCity WHERE CityID =' + str(CityID)).fetchall()
        if row:
            return row[0][0]
        return False

    @staticmethod
    def convertStateId(StateID, access):
        row = access.execute('select State from tblState WHERE StateID =' + str(StateID)).fetchall()
        if row:
            return row[0][0]
        return False

    @staticmethod
    def convertCountryId(CountryID, access):
        row = access.execute('select Country from tblCountry WHERE CountryID =' + str(CountryID)).fetchall()
        if row:
            return row[0][0]
        return False