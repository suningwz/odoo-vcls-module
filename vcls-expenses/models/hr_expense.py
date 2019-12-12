# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class HrExpense(models.Model):

    _inherit = "hr.expense"

    is_product_employee = fields.Boolean(related='product_id.is_product_employee', readonly=True, string="Product Employee")

    """type = fields.Selection([
        ('project', 'Billable'),
        ('admin', 'Non-Billable'),
        #('mobility', 'Mobility'),
    ], 
    related = 'sheet_id.type')"""

    product_list = fields.Char(
        store = False,
        compute = '_get_product_list',
    )
    

    project_id = fields.Many2one(
        'project.project', 
        related='sheet_id.project_id',
    )

    @api.model
    def _setup_fields(self):
        super(HrExpense, self)._setup_fields()
        self._fields['unit_amount'].states = None
        self._fields['unit_amount'].readonly = False
        self._fields['product_uom_id'].readonly = True
    
    @api.multi
    @api.depends('employee_id','project_id')
    def _get_product_list(self):
        for expense in self:
            products = self.env['product.product'].search([('can_be_expensed', '=', True),'|',('company_id','=',False),('company_id','=',expense.employee_id.company_id.id)])
            #_logger.info("{}".format(products.mapped('id')))
            product_list = "["
            for item in products:
                product_list += "'{}',".format(item.id)
            product_list += "]"
            expense.product_list = products.mapped('id')

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

    @api.multi
    def action_move_create(self):
        expenses_by_company = {}
        for expense in self:
            expenses_by_company.setdefault(expense.company_id, self.env["hr.expense"])
            expenses_by_company[expense.company_id] |= expense
        results = {}
        for company, groupped_expenses in expenses_by_company.items():
            result = super(HrExpense, groupped_expenses.with_context(
                force_company=company.id,
                default_company_id=company.id,
            )).action_move_create()
            results.update(result)
        return results

    @api.multi
    def _prepare_move_values(self):
        move_values = super(HrExpense, self)._prepare_move_values()
        move_values['company_id'] = self.sheet_id.company_id.id or move_values['company_id']
        return move_values

    @api.constrains('company_id', 'sheet_id.company_id')
    def _check_expenses_same_company(self):
        for expense in self:
            if not expense.sheet_id or not expense.company_id:
                continue
            if expense.sheet_id.company_id != expense.company_id:
                raise ValidationError(
                    _('Error! Expense company must be the same as the report company.'))
            if expense.account_id.company_id != expense.company_id:
                raise ValidationError(
                    _('Error! Expense company must be the same as the account company.'))
