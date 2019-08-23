# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'


    #################
    # CUSTOM FIELDS #
    #################

    type = fields.Selection([
        ('project', 'Project'),
        ('admin', 'Admin')
    ], 
    required = True, string = 'Type')

    project_id = fields.Many2one(
        'project.project', 
        string = 'Related Project'
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 
        string = 'Analytic Account',
        required = True
    )

    ######################
    # OVERWRITTEN FIELDS #
    ######################
    user_id = fields.Many2one(
        'res.users', 
        'Approver', 
        readonly=True, 
        copy=False, 
        states={'draft': [('readonly', False)]}, 
        track_visibility='onchange', 
        oldname='responsible_id',
        compute = '_compute_user_id'
    )

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('type', 'project_id', 'employee_id')
    def _compute_user_id(self):
        for record in self:
            if record.type == 'project':
                if record.project_id:
                    record.user_id = record.project_id.user_id
            else:
                if record.employee_id:
                    record.user_id = record.employee_id.parent_id.user_id