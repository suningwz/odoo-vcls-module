# -*- coding: utf-8 -*-

#Python Imports
from datetime import datetime, time
#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class LeaveAllocation(models.Model):
    
    _inherit = 'hr.leave.allocation'
   
    #used to customise selection domain according to the selected employee company
    employee_company_id = fields.Many2one(
        related='employee_id.company_id',
        String='Employee Company',)
    
    #As we removed some record rules, let's ensure there's no crosstalk between companies
    @api.constrains('number_of_days')
    def _check_company(self):
        for rec in self:  
            #Ensure the company_id is matching between the employee and the leave type
            if (rec.holiday_type=='employee') and (rec.employee_company_id != rec.holiday_status_id.company_id):
                raise ValidationError("The selected leave type is not related to the same company that the selected employee.")
    