# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'


    #################
    # CUSTOM FIELDS #
    #################

    type = fields.Selection([
        ('project', 'Project'),
        ('admin', 'Admin'),
        #('mobility', 'Mobility'),
    ], 
    required=True, string='Type', default='admin')

    # we link parent projects only
    project_id = fields.Many2one(
        'project.project', 
        string='Related Project',
        domain="[('parent_id','=',False)]",
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 
        string='Analytic Account',
    )

    sale_order_id = fields.Many2one(
        'sale.order', 
        string='Related Sale Order',
    )

    company_id = fields.Many2one(
        related='employee_id.company_id'
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
        compute='_compute_user_id'
    )

    @api.constrains('journal_id', 'journal_id.company_id', 'company_id')
    def _check_expense_sheet_same_company(self):
        for sheet in self:
            if not sheet.company_id or not sheet.journal_id:
                continue
            if sheet.journal_id.company_id != sheet.company_id:
                raise ValidationError(
                    _('Error! The journal company must be the same as the expense company.'))

    @api.multi
    def approve_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_user'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))
        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'approve', 'user_id': responsible_id})
        self.activity_update()

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
                # line manager to be the approver
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
            _logger.info("EXPENSE PROJECT {}".format(rec.type))
            if rec.project_id:
                # grab analytic account from the project
                if rec.type == 'admin':
                    rec.analytic_account_id = rec.project_id.analytic_account_id
                    rec.sale_order_id = False

                # we look for the SO in case of project (to be able to re-invoice)
                elif rec.type == 'project':
                    so = self.env['sale.order'].search([('project_id','=',rec.project_id.id)],limit=1)
                    if so:
                        rec.sale_order_id = so.id
                    else:
                        rec.sale_order_id = False
                    rec.analytic_account_id = False

                else:
                    rec.sale_order_id = False
                    rec.analytic_account_id = False          

    @api.multi
    def open_pop_up_add_expense(self):
        for rec in self:
            action = self.env.ref('vcls-expenses.action_pop_up_add_expense').read()[0]
            if rec.type == 'admin':
                action['context'] = {
                    'default_employee_id': rec.employee_id.id,
                    'default_analytic_account_id': rec.analytic_account_id.id,
                    'default_sheet_id': rec.id}
            elif rec.type == 'project':
                action['context'] = {
                    'default_employee_id': rec.employee_id.id,
                    'default_sale_order_id': rec.sale_order_id.id,
                    'default_sheet_id': rec.id}
            return action
          
    """ We override this to ensure a default journal to be properly updated """
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.address_id = self.employee_id.sudo().address_home_id
        self.department_id = self.employee_id.department_id
        #self.user_id = self.employee_id.expense_manager_id or self.employee_id.parent_id.user_id
        self.journal_id = self.env['account.journal'].search([('type', '=', 'purchase'),('company_id', '=', self.employee_id.company_id.id)], limit=1)
        self.bank_journal_id = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']),('company_id', '=', self.employee_id.company_id.id)], limit=1)

    

