# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Employee(models.Model):
    
    _inherit = 'hr.employee'

    default_rate_ids = fields.Many2many(
        'product.template',
        string='Default Rates',
        domain="[('seniority_level_id','!=',False)]",
    )

    seniority_level_id = fields.Many2one(
        comodel_name='hr.employee.seniority.level',
        compute='_compute_default_seniority',
        string='Default Seniority',
    )

    @api.depends('default_rate_ids')
    def _compute_default_seniority(self):
        for emp in self:
            if emp.default_rate_ids:
                emp.seniority_level_id = emp.default_rate_ids[0].seniority_level_id
