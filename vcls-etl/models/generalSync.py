# -*- coding: utf-8 -*-

from odoo import models, fields, api

import datetime, pytz

from abc import ABC,abstractmethod

class KeyNotFoundError(Exception):
    pass

class ETLMap(models.Model):
    _name = 'etl.sync.keys'
    _description = 'Mapping table to link Odoo ID with external ID'
    # Helsinki
    odooId = fields.Char(readonly = True)
    externalId = fields.Char(readonly = True)
    isUpdate = fields.Boolean(default = False)
    syncRecordId = fields.Many2one('etl.sync.mixin', readonly = True)

    # foutre les fonctions de mappage ici

class GeneralSync(models.AbstractModel):
    _name = 'etl.sync.mixin'
    _description = 'This model represents an abstract parent class used to manage ETL'
    
    keys = fields.One2many('etl.sync.keys','syncRecordId', readonly = True)
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





