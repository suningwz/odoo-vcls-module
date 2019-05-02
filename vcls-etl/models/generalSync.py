# -*- coding: utf-8 -*-

from odoo import models, fields, api

import datetime, pytz
from abc import ABC,abstractmethod

class KeyNotFoundError(Exception):
    pass

class ETLMap(models.Model):
    _name = 'etl.sync.keys'
    # Helsinki
    odooId = fields.Char(readonly = True)
    externalId = fields.Char(readonly = True)
    syncRecordId = fields.Many2one('etl.sync.mixin', readonly = True) # -> need testing

class GeneralSync(models.AbstractModel):
    _name = 'etl.sync.mixin'
    """ This model represents an abstract parent class used to manage ETL """
    keys = fields.One2many('etl.sync.keys','syncRecordId', readonly = True) # Not rightly declared -> error
    lastRun = fields.DateTime(readonly = True)

    def getLastRun(self):
        return self.lastRun
    
    def setNextRun(self):
        self.lastRun = datetime.datetime.now(pytz.timezone('GMT'))
    
    def getStrLastRun(self):
        if not self.lastRun:
            return '2000-01-01T00:00:00.00+0000'
        return self.lastRun.strftime("%Y-%m-%dT%H:%M:%S.00+0000")
    
    def getLastUpdate(self, OD_id):
        odooObject = self.partner.browse(OD_id)
        return odooObject.__last_update.strftime("%Y-%m-%dT%H:%M:%S.00+0000")

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
            record = self.env['etl.sync.keys'].search([('id', '=', key['odooId'])], limit = 1)
            if record.externalId == externalId:
                return record.odooId
        raise KeyNotFoundError
    
    @api.one
    def toExternalId(self, odooId):
        for key in self.keys:
            record = self.env['etl.sync.keys'].search([('id', '=', key['odooId'])], limit = 1)
            if record.odooId == odooId:
                return record.externalId
        raise KeyNotFoundError
    
    # Abstract method not implementable
    @abstractmethod
    def getFromExternal(self, translator, externalInstance):
        pass

    @abstractmethod
    def setToExternal(self, translator, externalInstance):
        pass

    @abstractmethod
    def update(self, item, translator):
        pass

    @abstractmethod
    def createRecord(self, item, translator):
        pass





