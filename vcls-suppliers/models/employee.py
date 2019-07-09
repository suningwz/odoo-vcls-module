# -*- coding: utf-8 -*-

#Python Imports
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class Employee(models.Model):
    
    _inherit = 'hr.employee'

    employee_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ('template', 'Template'),
        ],default = 'internal'
    )

    @api.model
    def create(self, vals):
        result = super(Employee, self).create(vals)
        if 'employee_type' in vals:
            if result.employee_type == 'external':
                type_id = self.env.ref('vcls-suppliers.contract_type_project_supplier').id
                job_id = self.env.ref('vcls-suppliers.job_project_supplier').id     
                resource_calendar_id = self.env["resource.calendar"].search([('company_id','=',result.company_id.id),
                                                                            ('effective_percentage','=', 1)],limit=1).id
                if resource_calendar_id:
                    if result.employee_start_date:
                        count = len(self.env['hr.contract'].search([('employee_id','=',result.id)]))
                        contract_name = "[{} | {:02}']".format(result.name,count+1)
                        contract = self.env['hr.contract'].sudo().create({
                                                        'name':contract_name,
                                                        'active': False,
                                                        'employee_id': result.id,
                                                        'type_id': type_id,
                                                        'job_id':job_id,
                                                        'company_id':result.company_id.id,
                                                        'date_start':result.employee_start_date,
                                                        'resource_calendar_id':resource_calendar_id})
                        result.contract_id = contract.id
                        
                    else:
                        raise ValidationError("Please enter an Employee Start Date")
                else:
                    raise ValidationError("No resource calendar for {} with 100{} effective".format(result.company_id.name,'%'))
        return result