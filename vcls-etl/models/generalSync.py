# -*- coding: utf-8 -*-

from odoo import models, fields, api

import datetime, pytz

from abc import ABC,abstractmethod

class KeyNotFoundError(Exception):
    pass

class ETLMap(models.Model):
    _name = 'etl.sync.keys'
    _description = 'tbd'
    # Helsinki
    odooId = fields.Char(readonly = True)
    externalId = fields.Char(readonly = True)
    isUpdate = fields.Boolean(default = False)
    existInExternal = fields.Boolean(default = False)
    existInOdoo = fields.Boolean(default = False)
    syncRecordId = fields.Many2one('etl.sync.mixin', readonly = True) # -> need testing

class GeneralSync(models.AbstractModel):
    _name = 'etl.sync.mixin'
    _description = 'This model represents an abstract parent class used to manage ETL'
    
    keys = fields.One2many('etl.sync.keys','syncRecordId', readonly = True) # Not rightly declared -> error
    lastRun = fields.Datetime(readonly = True)

    def setNextRun(self):
        self.lastRun = fields.Datetime.from_string(datetime.datetime.now(pytz.timezone("GMT")).strftime("%Y-%m-%d %H:%M:%S.00+0000"))
    
    def getStrLastRun(self):
        if not self.lastRun:
            return fields.Datetime.from_string('2000-01-01 00:00:00.000000+00:0')
        return self.lastRun
    

    @api.model
    def getLastUpdate(self, OD_id):
        partner = self.env['res.partner']
        odid = int(OD_id[0])
        record = partner.browse([odid])
        return str(record.write_date)

    @staticmethod
    def isDateOdooAfterExternal(dateOdoo, dateExternal):
        return dateOdoo >= dateExternal
    
    @api.one
    def addKeys(self, externalId, odooId):
        self.keys = [(0, 0,  { 'odooId': odooId, 'externalId': externalId })]
    # need test
    @api.one
    def updateKey(self, externalId):
        for key in self.keys:
            if key.externalId == externalId:
                key.isUpdate = True
    @api.one
    def allIsUpdated(self):
        for key in self.keys:
            if not key.isUpdate:
                return False
        return True
    @api.one
    def allNotIsUpdate(self):
        for key in self.keys:
            key.isUpdate = False
    @api.one
    def getisUpdate(self, externalId):
        for key in self.keys:
            if key.externalId == externalId:
                return key.isUpdate

    @api.one
    def toOdooId(self, externalId):
        for key in self.keys:
            if key.externalId == externalId:
                return key.odooId
        raise KeyNotFoundError
    
    @api.one
    def toExternalId(self, odooId):

        for key in self.keys:
            if key.odooId == odooId:
                return key.externalId
        raise KeyNotFoundError
    
    @api.one
    def initExistField(self):
        for key in self.keys:
            key.existInExternal = False
            key.existInOdoo = False
    
    @api.one
    def externalExist(self,externalId):
        for key in self.keys:
            if key.externalId == externalId:
                key.existInExternal = True
    @api.one
    def odooExist(self,odooId):
        for key in self.keys:
            if key.odooId == odooId:
                key.existInOdoo = True

    @api.one
    def deleteKeys(self):
        for key in self.keys:
            if not key.existInOdoo or not key.existInExternal:
                key.unlink()

    # Abstract method not implementable
    @abstractmethod
    def getFromExternal(self, translator, externalInstance, fullUpdate,updateKeyTables, createInOdoo, updateInOdoo):
        pass

    @abstractmethod
    def setToExternal(self, translator, externalInstance, time, createRevert, updateRevert):
        pass

    @abstractmethod
    def update(self, item, translator):
        pass

    @abstractmethod
    def createRecord(self, item, translator):
        pass





