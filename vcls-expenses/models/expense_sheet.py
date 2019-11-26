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

    company_id = fields.Many2one(
        related = 'employee_id.company_id'
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

    @api.onchange('project_id')
    def change_project(self):
        for rec in self:
            if rec.project_id and rec.project_id.analytic_account_id:
                rec.analytic_account_id = rec.project_id.analytic_account_id.id

    @api.multi
    def open_pop_up_add_expense(self):
        for rec in self:
            action = self.env.ref('vcls-expenses.action_pop_up_add_expense').read()[0]
            action['context'] = {'default_employee_id': rec.employee_id.id,
                                 'default_analytic_account_id': rec.analytic_account_id.id,
                                 'default_sheet_id': rec.id}
            return action

class HrExpense(models.Model):

    _inherit = "hr.expense"

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'hr.expense'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr.expense', 'default_res_id': self.id}
        res['view_id'] = self.env['ir.ui.view'].ref('view_hr_expense_attachment')
        res['target'] = 'new'
        return res