# -*- coding: utf-8 -*-
#Python Imports
from datetime import date, datetime, time
import xlsxwriter
import base64

#Odoo Imports
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class BillabilityExport(models.Model):
    _name = 'export.billability'
        
    """ This model represents an export of employees containing information required to compute capacity of the resource over a particular period. """

    name = fields.Char(readonly = True)
    active = fields.Boolean(default=True)
    
    start_date = fields.Date(
        string = 'Date from',
        required = True,
        )
    
    end_date = fields.Date(
        string = 'Date to',
        required = True,
        )
    
    attachment_id = fields.Many2one(
        'ir.attachment',
        string = 'Excel File',
        readonly = True,
        )
    
    #internal/external partner to share the info with
    partner_ids = fields.Many2many(
        'res.partner',
        string = 'Audience',
        )
    
    ################
    # CRUD METHODS #
    ################
    
    #At export creation, we generate the uid, and call the line create methods
    @api.model
    def create(self,vals):
        
        #export is created
        export=super().create(vals)
        
        #Build name
        count = len(self.env['export.billability'].search([('start_date','=',export.start_date),('end_date','=',export.end_date)]))
        export.name = "{:{dfmt}}_{:{dfmt}}_BillabilityExport_{:02}".format(export.start_date,export.end_date,count,dfmt='%Y%m%d')
        
        self.generate_excel(self.build_data)
        
        return export
    
    def build_data(self):
        pass
           