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
        
    """ This model represents an abstract parent class used to manage excel reports"""
    
    name = fields.Char()
    active = fields.Boolean(default=True)
    
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
            'name': 'export_payroll',
            'url': '/web/content/%s/%s' % (self.attachment_id.id, self.attachment_id.name),
            }
    
    def generate_excel(self,data=[{'col_name':'','value':''}]):
        self.ensure_one()
        #build book and sheet
        filename = self.name + '.xlsx'
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet() 
        
        #write Header row
        
        """
        for export in self:
            
            #build file in memory
            filename = self.name + '.xlsx'
            workbook = xlsxwriter.Workbook(filename)
            
            self.build_worksheet(workbook)
            workbook.close()
            
            #Encode and save as attachment
            with open(filename, "rb") as f:
                data = f.read()
                encoded = base64.b64encode(data)
                attachment_data = {
                            'res_id': export.id,
                            'res_model': 'export.payroll',
                            'company_id': export.company_id.id,
                            'name': self.name,
                            'type': 'binary',
                            'datas_fname': filename,
                            'datas': encoded,
                        }
                export.attachment_id = self.env['ir.attachment'].create(attachment_data)
                export.is_generated = True
        """