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
    syncRecordId = fields.Many2one('?etl.sync.mixin', readonly = True)

    state = fields.Selection([
        ('upToDate', 'Up To Date'),
        ('needUpdateOdoo', 'Need Update In Odoo'),
        ('needUpdateExternal', 'Need Update In External'),
        ('needCreateOdoo', 'Need To Be Created In Odoo'),
        ('needCreateExternal', 'Need To Be Created In External')],
        string='State',
        default='upToDate' # For existing keys
    )

    @api.one
    def setState(self, state):
        self.state = state

    # foutre les fonctions de mappage ici

class GeneralSync(models.AbstractModel):
    _name = 'etl.sync.mixin'
    _description = 'This model represents an abstract parent class used to manage ETL'
    
    keys = fields.One2many(comodel_name = 'etl.sync.keys', inverse_name ='syncRecordId', readonly = True)
    lastRun = fields.Datetime(readonly = True)

    def setNextRun(self):
        self.lastRun = fields.Datetime.from_string(datetime.datetime.now(pytz.timezone("GMT")).strftime("%Y-%m-%d %H:%M:%S.00+0000"))
        print(self.lastRun)
    
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
    def addKeys(self, externalId, odooId, state):
        self.keys = [(0, 0,  { 'odooId': odooId, 'externalId': externalId, 'state': state })]

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
    def getKeyFromOdooId(self, odooId):
        for key in self.keys:
            if key.odooId == odooId:
                return key
        raise KeyNotFoundError
    
    @api.one
    def getKeyFromExtId(self, externalId):
        for key in self.keys:
            if key.externalId == externalId: 
                return key
        raise KeyNotFoundError

    @abstractmethod
    def updateKeyTables(self):
        pass
    @abstractmethod
    def updateOdooInstance(self):
        pass
    
    @abstractmethod
    def needUpdateExternal(self):
        pass
    
    ####################

    @abstractmethod
    def updateKeyTable(self, externalInstance):
        pass




