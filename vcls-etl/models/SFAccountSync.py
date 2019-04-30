
from odoo import models, fields, api

class SFAccountSync(models.Model):
    _name = 'etl.salesforce.account'
    _inherit = 'etl.sync.mixin'

    def getFromExternal(self, translator, externalInstance):
        pass
    



    def setToExternal(self, translator, externalInstance):
        pass