# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class Leads(models.Model):

    _inherit = 'crm.lead'

    marketing_project_id = fields.Many2one(
        comodel_name = 'project.project',
        string = "Lead Source",
        domain = [('project_type','=','marketing')]
    )

    marketing_task_id = fields.Many2one(
        comodel_name = 'project.task',
        string = "Opted-In Campaign",
        domain = [('task_type','=','marketing')]
    )

    marketing_task_out_id = fields.Many2one(
        comodel_name = 'project.task',
        string = "Opted-Out Campaign",
        domain = [('task_type','=','marketing')]
    )

    opted_in_date = fields.Datetime(
        string = 'Opted In Date',
        #default = lambda self: self.create_date,
    )

    opted_out_date = fields.Datetime(
        string = 'Opted Out Date', 
        related = 'marketing_task_out_id.create_date',
    )

    gdpr_status = fields.Selection(
        [
            ('undefined', 'Undefined'),
            ('in', 'In'),
            ('out', 'Out'),
        ],
        string = 'GDPR Status',
        compute = '_compute_gdpr_status',
    )

    @api.depends('marketing_task_id', 'marketing_task_out_id')
    def _compute_gdpr_status(self):
        for record in self:
            if record.marketing_task_id and not record.marketing_task_out_id:
                record.gdpr_status = 'in'
            elif record.marketing_task_out_id:
                record.gdpr_status = 'out'
            else:
                record.gdpr_status = 'undefined'

