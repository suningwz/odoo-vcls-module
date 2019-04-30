# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime, pytz

class KeyNotFoundError(Exception):
    pass

class ETLMap(models.Model):
    _name = 'etl.sync.keys'
    # Helsinki
    odooId = fields.Char(readonly = True)
    externalId = fields.Char(readonly = True)


class GeneralSync(models.AbstractModel):
    _name = 'etl.sync.mixin'
    """ This model represents an abstract parent class used to manage ETL """

    keys = fields.One2many('etl.sync.keys', readonly = True)
    lastRun = fields.Date(readonly = True)

    def getLastRun(self):
        return self.lastRun
    
    def setNextRun(self):
        self.lastRun = datetime.datetime.now(pytz.timezone('GMT'))
    
    def getStrLastRun(self):
        return self.lastRun.strftime("%Y-%m-%dT%H:%M:%S.00+0000")
    
    @staticmethod
    def isDateOdooAfterExternal(dateOdoo, dateExternal):
        return dateOdoo >= dateExternal
    
    @api.one
    def addKeys(self, externalId, odooId):
        self.keys = (0, 0,  { 'odooId': odooId, 'externalId': externalId })
    # need test

    @api.one
    def toOdooId(self, externalId):
        for key in self.keys:
            record = self.env['etl.sync.keys'].search([('id', '=', 'key')], limit = 1)
            if record.externalId == externalId:
                return record.odooId
        raise KeyNotFoundError
    
    @api.one
    def toExternalId(self, odooId):
        for key in self.keys:
            record = self.env['etl.sync.keys'].search([('id', '=', 'key')], limit = 1)
            if record.odooId == odooId:
                return record.externalId
        raise KeyNotFoundError
    
    # Abstract method not implementable
    '''
    def getFromExternal(self, translator, externalInstance):
        pass
    
    def setToExternal(self, translator, externalInstance):
        pass
    '''





