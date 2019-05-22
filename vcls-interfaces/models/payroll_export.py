# -*- coding: utf-8 -*-
#Python Imports
from datetime import date, datetime, time
import xlsxwriter
import base64

#Odoo Imports
from . import payroll_constants
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PayrollExport(models.Model):
    _name = 'export.payroll'
    _inherit = 'export.excel.mixin'
        
    """ This model represents a monthly payroll export per company. It contains the employee related export lines, the header info (inc. aggregated control values) as well as the methods to generate the related excel file """

    name = fields.Char(readonly = True)
    
    ### IDENTIFICATION FIELDS 
    
    company_id = fields.Many2one(
        'res.company',
        string = 'Company',
        required = True,
        )

    month = fields.Selection(
        string = 'Payroll Month',
        selection = '_selection_month',
        required = True,
        )
    
    start_date = fields.Date(
        string = 'Date from',
        required = True,
        )
    
    end_date = fields.Date(
        string = 'Date to',
        required = True,
        )
    
    custom_leave_dates = fields.Boolean(
        default = False,
        compute = '_compute_custom_leave_dates',
        store = True,
    )
    
    leave_start_date = fields.Date(
        string = 'Leave Period Start', 
        )
    
    leave_end_date = fields.Date(
        string = 'Leave Period End',
        )
    
    payment_date = fields.Date(
        string = 'Payment Date',
        required = True,
        )
    
    year = fields.Char(
        required = True,
        compute = '_compute_year',
        )
    
    employee_ids = fields.Many2many(
        'hr.employee',
        string = 'Employees',
        readonly = True,
        )
    
    #export lines
    line_ids = fields.One2many(
        'export.payroll.line',
        'export_id',
        string = 'Related Lines',
        readonly = True,
        )
    
    ### AGGREGATED FIELDS FOR QUICK CONTROL
    #Employee related
    count_employee = fields.Integer(
        string = 'Number of Employees',
        readonly = True,)
    
    count_lines = fields.Integer(
        string = 'Number of Export Lines',
        readonly = True,)
    
    count_fte = fields.Float(
        string = 'Total FTEs',
        readonly = True,)
    
    count_newcomer = fields.Integer(
        string = 'Number of Newcomers',
        readonly = True,
        )
    
    count_leavers = fields.Integer(
        string = 'Number of Leavers',
        readonly = True,
        )
    
    #Leaves related
    count_paid_leaves = fields.Integer(
        string = 'Number of Paid Leave Days',
        readonly = True,)
    
    count_unpaid_leaves = fields.Integer(
        string = 'Number of Unpaid Leave Days',
        readonly = True,)
    
    count_bank = fields.Integer(
        string = 'Number of Bank Holidays',
        readonly = True,)
    
    #Finance related
    currency_id = fields.Many2one(
        related = 'company_id.currency_id',
        string = "Currency",
        readonly = True,
        store = True,)
    
    total_payroll = fields.Monetary(
        string = 'Payroll Total Amount',
        compute = '_compute_total_payroll',
        readonly = True,
        )
    
    total_wage = fields.Monetary(
        string = 'Wages Amount',
        readonly = True,)
    
    total_benefit = fields.Monetary(
        string = 'Benefits Amount',
        readonly = True,)
    
    total_bonus = fields.Monetary(
        string = 'Over Variable Salaries Amount',
        readonly = True,)
    
    ###################
    # COMPUTE METHODS #
    ###################
    
    @api.depends('end_date')
    def _compute_year(self):
        for rec in self:
            if rec.end_date:
                rec.year = str(self.end_date.year)
            
    @api.depends('total_wage','total_benefit','total_bonus')
    def _compute_total_payroll(self):
        for rec in self:
            rec.total_payroll = rec.total_wage + rec.total_benefit + rec.total_bonus
    
    def _compute_employee_stats(self):
        for export in self:
            export.count_employee = len(export.employee_ids)
            export.count_newcomer = len(self.env['hr.employee'].search([('company_id.id','=',export.company_id.id),('employee_start_date','>=',export.start_date),('employee_start_date','<=',export.end_date)]))
            export.count_leavers = len(self.env['hr.employee'].search([('company_id.id','=',export.company_id.id),('employee_end_date','>=',export.start_date),('employee_end_date','<=',export.end_date)]))
            export.count_fte = sum(export.line_ids.mapped('working_percentage'))
            
    def _compute_financial_stats(self):
        for export in self:
            export.total_wage = sum(export.line_ids.mapped('prorated_salary'))/12
            export.total_benefit = sum(export.line_ids.mapped(lambda r: r.transport_allowance + r.car_allowance + r.lunch_allowance))
            export.total_bonus = sum(export.line_ids.mapped('total_bonus'))
    
    @api.onchange('start_date')
    def _set_leave_start(self):
        for export in self:
            export.leave_start_date = export.start_date

    @api.onchange('end_date')
    def _set_leave_end(self):
        for export in self:
            export.leave_end_date = export.end_date
    
    @api.depends('company_id')
    def _compute_custom_leave_dates(self):
        for export in self:
            if export.company_id == self.env.ref('base.main_company') or export.company_id == self.env.ref('vcls-hr.company_VCFR'):
                export.custom_leave_dates = True
            else:
                export.custom_leave_dates = False
        

    
    ################
    # CRUD METHODS #
    ################
    #At export creation, we generate the uid, and call the line create methods
    @api.model
    def create(self,vals):
        
        # EXPORT CREATION #
        #Build name
        company_id = vals.get('company_id')
        year = vals.get('end_date')[:4]
        month = vals.get('month')
        index = len(self.env['export.payroll'].search([('company_id.id','=',company_id),('month','=',month),('year','=',year)])) + 1
            
        short = self.env['res.company'].search([('id','=',company_id)]).short_name
        vals['name'] = "{}{}_{}_{:02}_PayrollExport".format(month,year,short,index)

        #export is created
        export=super().create(vals)

        #we update the notes in case of custom
        if export.custom_leave_dates:
            if export.notes:
                export.notes = " Leave Period: {} to {} | {}".format(export.leave_start_date, export.leave_end_date, export.notes)
            else:
                export.notes = " Leave Period: {} to {}".format(export.leave_start_date, export.leave_end_date)
        
        # LINES CREATION #
        #we search for elligible employees, i.e. the ones that were active at the export end_date 
        export.employee_ids = self.env['hr.employee'].with_context(active_test=False).search([('company_id.id','=',company_id),('employee_start_date','<=',export.end_date),('employee_start_date','!=',False),'|',('employee_end_date','=',False),('employee_end_date','>=',export.end_date)])
        
        #Raise error if an employee has no contract
        no_contract = export.employee_ids.filtered(lambda r: not r.contract_id.id > 0)
        if len(no_contract)>0:
            raise ValidationError("Impossible to Export, missing contract for employees ({})".format(no_contract.mapped('name')))
        
        export.line_ids = False
        for emp in export.employee_ids:
            export.line_ids += self.env['export.payroll.line'].sudo().create({
                    'export_id':export.id,
                    'employee_id':emp.id,
                })
            
        export.count_lines = len(export.line_ids)
        #raise ValidationError('{}   ---- {} /// {}.{}.{}'.format(export.employee_ids,export.line_ids,len(export.employee_ids),len(export.line_ids),export.count_lines))
        export._compute_employee_stats()
        export._compute_financial_stats()
        
        return export
    
    ##################
    # BUTTON METHODS #
    ##################
    def get_lines_action(self):
        for export in self:
            if export.company_id == export.env.ref('base.main_company'):
                return self.env.ref('vcls-interfaces.action_export_payroll_line_FR').read()[0]
            elif self.company_id == self.env.ref('vcls-hr.company_VCFR'):
                return self.env.ref('vcls-interfaces.action_export_payroll_line_FR').read()[0]
            elif self.company_id == self.env.ref('vcls-hr.company_VCCH'):
                return self.env.ref('vcls-interfaces.action_export_payroll_line_CH').read()[0]
            elif self.company_id == self.env.ref('vcls-hr.company_VCINC'):
                return self.env.ref('vcls-interfaces.action_export_payroll_line_INC').read()[0]
            elif self.company_id == self.env.ref('vcls-hr.company_VCPVT'):
                return self.env.ref('vcls-interfaces.action_export_payroll_line_PVT').read()[0]
            elif self.company_id == self.env.ref('vcls-hr.company_RRG'):
                return self.env.ref('vcls-interfaces.action_export_payroll_line_UK').read()[0]
            elif self.company_id == self.env.ref('vcls-hr.company_CWLS'):
                return self.env.ref('vcls-interfaces.action_export_payroll_line_UK').read()[0]
            else:
                return self.env.ref('vcls-interfaces.action_export_payroll_line_FR').read()[0]

            
    #####################
    # SELECTION METHODS #
    #####################
    
    @api.model
    def _selection_month(self):
        return [
            ('Jan','January'),
            ('Feb','February'),
            ('Mar','March'),
            ('Apr','April'),
            ('May','May'),
            ('Jun','June'),
            ('Jul','July'),
            ('Aug','August'),
            ('Sep','September'),
            ('Oct','October'),
            ('Nov','November'),
            ('Dec','December'),
        ]
    
    def generate_excel(self):
        for export in self:
            
            #build file in memory
            filename = export.name + '.xlsx'
            workbook = xlsxwriter.Workbook(filename)
            #raise ValidationError('{}'.format(filename))
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
                            'name': filename,
                            'type': 'binary',
                            'datas_fname': filename,
                            'datas': encoded,
                        }
                export.attachment_id = self.env['ir.attachment'].create(attachment_data)
                export.is_generated = True

    def build_worksheet(self, workbook):
        
        worksheet = workbook.add_worksheet()
        wrap_format = workbook.add_format({'text_wrap': True})
        std_format = workbook.add_format()
        
        header = self.get_header()
        row_count = len(self.line_ids)
       
        
        # year month payment_date
        col = 0
        for h in header:
            worksheet.write(0, col, h['h_name'])
            
            #if this is an export source field, we repeat the same value in the whole column
            if h['field_name'] == 'year':
               for row in range(row_count):
                    worksheet.write(row + 1, col, self.year)
            elif h['field_name'] == 'month':
                for row in range(row_count):
                    worksheet.write(row + 1, col, self.month)
            elif h['field_name'] == 'payment_date':
                for row in range(row_count):
                    worksheet.write(row + 1, col, self.payment_date.strftime('%d %b %y'))
            
            #if the field is lne related, then loop the lines        
            else:
                format = std_format
                if h['field_name'].find('_info')>0:
                    format = wrap_format
                    
                values = self.line_ids.mapped(h['field_name'])
                for row in range(row_count):
                    worksheet.write(row + 1, col, values[row],format)
                    
            col += 1
            
    def  get_header(self):
        # Voisin WW
        if self.company_id == self.env.ref('base.main_company'):
            return payroll_constants.PAYROLL_FR_V1
        if self.company_id == self.env.ref('vcls-hr.company_VCFR'):
            return payroll_constants.PAYROLL_FR_V1
        if self.company_id == self.env.ref('vcls-hr.company_VCCH'):
            return payroll_constants.PAYROLL_CH_V1
        if self.company_id == self.env.ref('vcls-hr.company_RRG'):
            return payroll_constants.PAYROLL_UK_V1
        if self.company_id == self.env.ref('vcls-hr.company_CWLS'):
            return payroll_constants.PAYROLL_UK_V1
        if self.company_id == self.env.ref('vcls-hr.company_VCPVT'):
            return payroll_constants.PAYROLL_PVT_V1
        if self.company_id == self.env.ref('vcls-hr.company_VCINC'):
            return payroll_constants.PAYROLL_INC_V1
        else:
            return payroll_constants.PAYROLL_FR_V1