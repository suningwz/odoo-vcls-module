# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class Survey(models.Model):
    
    _inherit = 'survey.survey'

    privacy_mode = fields.Selection(
        string = "Privacy",
        selection=[
            ('normal', 'Normal'),
            ('mgmt', 'Management Line'),
        ],
        default='normal',
    )

class UserInput(models.Model):
    
    _inherit = 'survey.user_input'

    authorized_reader_ids = fields.Many2many(
        comodel_name = 'res.users',
        compute = '_compute_authorized_reader',
        store=True,
    )

    @api.depends('partner_id','survey_id.privacy_mode')
    def _compute_authorized_reader(self):
        for answer in self:
            if answer.survey_id.privacy_mode == 'mgmt':
                #we look for the employee management line
                employee = self.env['hr.employee'].search(['related_partner_id','=',answer.partner_id],limit=1)
                if employee:
                    answer.authorized_reader_ids = employee.lm_ids

class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"
    
    @api.multi
    def cancel_appraisal(self):
        self = self.with_context(safe_unlink=True)
        return super(HrAppraisal, self).cancel_appraisal()