# -*- coding: utf-8 -*-
#Python Imports
from datetime import date, datetime, time
import xlsxwriter
import base64

#Odoo Imports
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ExcelExportMixin(models.AbstractModel):
    _name = 'export.excel.mixin'
    _description = 'This model represents an abstract parent class used to manage excel reports'
    
    name = fields.Char()
    active = fields.Boolean(default=True)
    
    start_date = fields.Date(
        string = 'Date from',
        )
    
    end_date = fields.Date(
        string = 'Date to',
        )
    
    #attachment
    attachment_id = fields.Many2one(
        'ir.attachment',
        string = 'Excel File',
        readonly = True,
        )
    
    is_generated = fields.Boolean(
        readonly = True,
        default = False,
        )
    
    notes = fields.Char()
    
    #internal/external partner to share the info with
    partner_ids = fields.Many2many(
        'res.partner',
        string = 'Audience',
        )
    
    ################
    # TOOL METHODS #
    ################

    def get_excel(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'get_export_file',
            'url': '/web/content/%s/%s?download=true' % (self.attachment_id.id, self.attachment_id.name),
            }
    
    def generate_excel(self,data=[{'col1_name':'','col2name':''}]):
        self.ensure_one()
        #build book and sheet
        filename = self.name + '.xlsx'
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet() 
        
        #write Header row
        j = 0
        for key,value in data[0].items():
            worksheet.write(0, j, key)
            j += 1
            
        #write the data rows
        i = 1
        for row in data:
            j = 0
            for key,value in row.items():
                worksheet.write(i, j, value)
                j += 1
            i += 1
        
        #close & encode
        workbook.close() 
            
        try:
            company = self.company_id.id
        except:
            company = False
            
        #Encode and save as attachment
        with open(filename, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data)
            attachment_data = {
                'res_id': self.id,
                'res_model': self._name,
                'company_id': company,
                'name': filename,
                'type': 'binary',
                'datas_fname': filename,
                'datas': encoded,
            }
            self.attachment_id = self.env['ir.attachment'].create(attachment_data)
            self.is_generated = True
            
    ######################
    # VALIDATION METHODS #
    ######################
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for export in self:
            if export.start_date and export.end_date:
                if export.start_date > export.end_date:
                    raise ValidationError("Date configuration error: Date to: {} is before Date from: {}".format(export.start_date,export.end_date))
       