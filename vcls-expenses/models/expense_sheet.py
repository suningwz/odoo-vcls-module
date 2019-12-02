# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'


    #################
    # CUSTOM FIELDS #
    #################

    type = fields.Selection([
        ('project', 'Project'),
        ('admin', 'Admin'),
        ('mobility', 'Mobility'),
    ], 
    required = True, string = 'Type')

    #we link parent projects only
    project_id = fields.Many2one(
        'project.project', 
        string = 'Related Project',
        domain="[('parent_id','=',False)]",
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 
        string = 'Analytic Account',
        required = True
    )

    sale_order_id = fields.Many2one(
        'sale.order', 
        string = 'Related Sale Order',
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
                    record.user_id = False
            else:
                #line manager to be the approver
                if record.employee_id:
                    record.user_id = record.employee_id.parent_id.user_id
                else:
                    record.user_id = False
    
    @api.onchange('type')
    def change_type(self):
        for sheet in self:
            sheet.project_id=False

    @api.onchange('project_id')
    def change_project(self):
        for rec in self:
            if rec.project_id and rec.project_id.analytic_account_id:
                rec.analytic_account_id = rec.project_id.analytic_account_id.id
                #we look for the SO in case of project (to be able to re-invoice)
                if rec.type == 'project':
                    so = self.env['sale.order'].search([('project_id','=',rec.project_id.id)],limit=1)
                    if so:
                        rec.sale_order_id = so.id
                    else:
                        rec.sale_order_id = False
                else:
                    rec.sale_order_id = False          

    @api.multi
    def open_pop_up_add_expense(self):
        for rec in self:
            action = self.env.ref('vcls-expenses.action_pop_up_add_expense').read()[0]
            action['context'] = {'default_employee_id': rec.employee_id.id,
                                 'default_analytic_account_id': rec.analytic_account_id.id,
                                 'default_sale_order_id': rec.sale_order_id.id,
                                 'default_sheet_id': rec.id}
            return action

class HrExpense(models.Model):

    _inherit = "hr.expense"

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('vcls-expenses', 'action_attachment_expense')
        res['domain'] = [('res_model', '=', 'hr.expense'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr.expense', 'default_res_id': self.id}
        res['view_mode'] = 'form'
        res['view_id'] = self.env.ref('vcls-expenses.view_hr_expense_attachment')
        res['target'] = 'new'
        return res