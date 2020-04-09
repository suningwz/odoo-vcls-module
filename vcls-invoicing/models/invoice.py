# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import lxml
import base64
from itertools import groupby
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from collections import OrderedDict
from odoo.tools import OrderedSet

import logging
_logger = logging.getLogger(__name__)

DRAFTINVOICE = '_DraftInvoice'
ACTIVITYREPORT = '_ActivityReport'


class Invoice(models.Model):
    _inherit = 'account.invoice'

    #def _get_default_po_id(self):
        #return self.env['sale.order'].search([('invoice_ids', 'in', [self.id])], limit=1).po_id

    po_id = fields.Many2one('invoicing.po',
                            #default = _get_default_po_id,
                            string ='Client PO ref.')

    user_id = fields.Many2one(
        'res.users',
        string='Invoicing Administrator',
        related='commercial_partner_id.invoice_admin_id',
        )

    invoice_sending_date = fields.Datetime()

    temp_name = fields.Char(
        compute='compute_temp_name',
    )
    program_name = fields.Char(
        compute='compute_program_name',
    )
    program_description = fields.Char(
        compute='compute_program_description',
    )
    invoice_is_program = fields.Boolean()


    period_start = fields.Date()
    lc_laius = fields.Text()
    scope_of_work = fields.Text()

    vcls_due_date = fields.Date(string='Custom Due Date', compute='_compute_vcls_due_date')
    #origin_sale_orders = fields.Char(compute='compute_origin_sale_orders',string='Origin')

    ready_for_approval = fields.Boolean(default=False)

    invoice_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'account.invoice'),('name', 'ilike', 'invoice')])
    activity_report_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'account.invoice'),('name', 'ilike', 'activity')])

    report_count = fields.Integer(
        compute='_compute_attachment_count',
        default = 0,
    )

    draft_count = fields.Integer(
        compute='_compute_attachment_count',
        default=0,
    )

    communication_rate = fields.Float()

    """bank_account_id = fields.Many2one(
        'res.partner.bank', string='Bank Account',
        help='Company Bank Account Number to which the invoice will be paid.',
    )"""

    partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Partner Bank Account',
    )

    merge_subtask = fields.Boolean()

    parent_analytic_account_id = fields.Many2one(
        'account.analytic.account',
    )

    @api.multi
    def get_last_report(self):
        self.ensure_one()
        last_report_id = self.env['ir.attachment'].sudo().search([
            ('res_id', '=', self.id),
            ('name', 'like', DRAFTINVOICE)],
            limit=1, order='create_date desc'
        )
        if last_report_id:
            return {
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': '/web/content/%s/%s?download=true' % (last_report_id.id, last_report_id.name)
            }

    @api.multi
    def action_invoice_open(self):
        result = super(Invoice, self).action_invoice_open()
        if self.invoice_template:
            self.action_generate_draft_invoice()
        return result

    """@api.model
    def default_get(self, fields_list):
        result = super(Invoice, self).default_get(fields_list)
        company = self.env['res.company']._company_default_get()
        bank_accounts = company.bank_ids.filtered(lambda b: not b.currency_id or b.currency_id == company.currency_id)
        if bank_accounts:
            result['bank_account_id'] = bank_accounts[0].id
        return result

    @api.onchange('company_id', 'currency_id')
    def _on_change_currency(self):
        if not self.bank_account_id:
            bank_accounts = self.company_id.bank_ids.filtered(
                lambda b: not b.currency_id or b.currency_id == self.currency_id
            )
            self.bank_account_id = bank_accounts and bank_accounts[0] or False"""

    @api.depends('timesheet_limit_date', 'period_start')
    def compute_temp_name(self):
        for invoice in self:
            project_string = ""
            for project in invoice.project_ids:
                if not project.parent_id and project.sale_order_id and project.sale_order_id.internal_ref:
                    project_string += project.sale_order_id.internal_ref + ' | ' 
            invoice.temp_name = "{} from {} to {}".format(project_string,invoice.period_start,invoice.timesheet_limit_date)

    @api.multi
    def compute_program_name(self):
        list_projects = self.origin.split(', ')
        for invoice in self:
            if len(list_projects) > 1:
                self.invoice_is_program = True
            program_name = ""
            for project in invoice.project_ids:
                if project.program_id.name:
                    invoice.program_name = project.program_id.name

    @api.multi
    def compute_program_description(self):
        for invoice in self:
            program_description = ""
            for project in invoice.project_ids:
                if project.program_id.product_description:
                    invoice.program_description = project.program_id.product_description

    @api.multi
    def _compute_attachment_count(self):
        for invoice in self:
            drafts = self.env['ir.attachment'].search([('res_id', '=', self.id),('name', 'like', DRAFTINVOICE)])
            if drafts:
                invoice.draft_count = len(drafts)
            else:
                invoice.draft_count = 0

            reports = self.env['ir.attachment'].search([('res_id', '=', self.id),('name', 'like', ACTIVITYREPORT)])
            if reports:
                invoice.report_count = len(reports)
            else:
                invoice.report_count = 0

    
    @api.multi
    def _get_source_data(self,vals):
        self.ensure_one()
        #we initiate variables
        laius = ""
        sow = ""

        #loop in projects
        for project in self.project_ids:

            #get last  as laius if non exists
            if not vals.get('lc_laius',self.lc_laius):
                if project.summary_ids:
                    last_summary = project.summary_ids.sorted(lambda s: s.create_date, reverse=True)[0]
                    external_summary = self.html_to_string(last_summary.external_summary) \
                        if last_summary.external_summary else ''
                    if last_summary.create_date and external_summary:
                        laius += "Project Status on {}:\n{}\n\n".format(last_summary.create_date.date(), external_summary)
            else:
                laius = vals.get('lc_laius',self.lc_laius)

            # get sow if non exists
            if not vals.get('scope_of_work',self.scope_of_work):
                if project.scope_of_work:
                    sow += "{}\n".format(self.html_to_string(project.scope_of_work))
            else:
                sow = vals.get('scope_of_work', self.scope_of_work)

        return vals

    @api.multi
    def _get_activity_report_data(self, detailed=True):
        self.ensure_one()
        task_rate_matrix_data = {}
        project_rate_matrix_data = {}
        time_category_rate_matrix_data = {}
        product_obj = self.env['product.product']
        rate_product_ids = product_obj
        projects_row_data = OrderedDict()
        list_timesheet_to_compute = {}

        for timesheet_id in self.timesheet_ids:
            # check if so line is invoiced
            if not timesheet_id.so_line.qty_invoiced:
                continue
            project_id = timesheet_id.project_id

            if timesheet_id.task_id.parent_id:
                if timesheet_id.task_id.parent_id in list_timesheet_to_compute:
                    if timesheet_id.task_id[0] not in list_timesheet_to_compute[timesheet_id.task_id.parent_id[0]]:
                        list_timesheet_to_compute[timesheet_id.task_id.parent_id[0]] += [timesheet_id.task_id[0]]
                else:
                    list_timesheet_to_compute[timesheet_id.task_id.parent_id[0]] = [timesheet_id.task_id[0]]
            else: 
                if timesheet_id.task_id[0] in list_timesheet_to_compute:
                    if timesheet_id.task_id[0] not in list_timesheet_to_compute[timesheet_id.task_id[0]]:  # if the task is already in the list but is its own parent, put it a the begining of the list
                        # list_timesheet_to_compute[timesheet_id.task_id[0]] += [timesheet_id.task_id[0]]
                        list_timesheet_to_compute[timesheet_id.task_id[0]] = [timesheet_id.task_id[0]] + list_timesheet_to_compute[timesheet_id.task_id[0]]
                else:
                    list_timesheet_to_compute[timesheet_id.task_id[0]] = [timesheet_id.task_id[0]]

        # Here we have a dict key: parent_task_id, value: list of subtask_id (con include the parent task id if there is time coded on it)

        # for values in dict.values():
        for parent_task, list_tasks in list_timesheet_to_compute.items():
            number_tasks = len(list_tasks)
            print("NOMBRE DE TACHES   ========> ", number_tasks)
            for task_individual in list_tasks:
                total_hours_task = 0.0
                for timesheet_id in task_individual.timesheet_ids:
                    if self.merge_subtask and timesheet_id.task_id.parent_id:  # if the task has a parent and we want to merge
                        current_task_id = timesheet_id.task_id.parent_id
                    else:
                        current_task_id = timesheet_id.task_id

                    rate_product_id = timesheet_id.so_line.product_id
                    rate_product_ids |= rate_product_id
                    time_category_id = timesheet_id.time_category_id
                    unit_amount = timesheet_id.unit_amount

                    # project matrix data
                    project_rate_matrix_key = (project_id, rate_product_id)
                    project_rate_matrix_data.setdefault(project_rate_matrix_key, 0.)
                    project_rate_matrix_data[project_rate_matrix_key] += unit_amount
                    tasks_row_data = projects_row_data.setdefault(project_id, OrderedDict())

                    # task matrix data
                    task_rate_matrix_key = (project_id, current_task_id, rate_product_id)
                    # if timesheet_id.task_id.parent_id:
                    #     task_to_use = timesheet_id.task_id.parent_id
                    #     task_rate_matrix_key2 = (project_id, task_to_use, rate_product_id)
                    #     task_rate_matrix_data[task_rate_matrix_key2][1] += unit_amount
    
                    # task_rate_matrix_data.setdefault(task_rate_matrix_key, [0., parent_task])
                    task_rate_matrix_data.setdefault(task_rate_matrix_key, [0., 0.])
                    task_rate_matrix_data[task_rate_matrix_key][0] += unit_amount
                    task_rate_matrix_data[task_rate_matrix_key][1] += unit_amount
                    
                    # task_rate_matrix_data.setdefault(task_rate_matrix_key, 0.)
                    # task_rate_matrix_data[task_rate_matrix_key] += unit_amount

                    time_category_row_data = tasks_row_data.setdefault(current_task_id, [OrderedDict(), parent_task, number_tasks])
                    
                    # time_category_row_data = tasks_row_data.setdefault(current_task_id, OrderedDict()).copy()
                    # tasks_row_data[current_task_id] = parent_task
                    # tasks_row_data.setdefault(current_task_id, [OrderedDict(), parent_task])
                    time_category_row_data = time_category_row_data[0]

                    # time category matrix data
                    if detailed:
                        time_category_matrix_key = (project_id, current_task_id, time_category_id, rate_product_id)
                        time_category_rate_matrix_data.setdefault(time_category_matrix_key, 0.)
                        time_category_rate_matrix_data[time_category_matrix_key] += unit_amount
                        time_category_row_data.setdefault(time_category_id, None)



        # ORDRE DES COLONNES DE RATE
        # reorder rate_product_ids according to the richer one
        rate_product_ids = rate_product_ids
        rate_product_ids = product_obj.browse(OrderedSet([
            couple[1].id for couple in
            sorted(
                [(project_id, rate_product_id)
                    for project_id in projects_row_data.keys()
                    for rate_product_id in rate_product_ids],
                key=lambda key: project_rate_matrix_data[key],
                reverse=True
            )
        ]))
        return {
            'project_rate_matrix_data': project_rate_matrix_data,
            'task_rate_matrix_data': task_rate_matrix_data,
            'time_category_rate_matrix_data': time_category_rate_matrix_data,
            'rate_product_ids': rate_product_ids,
            'projects_row_data': projects_row_data,
        }



# # old functionnalities
#         list_timesheet = list_timesheet_to_compute.values()
#         result_list = []
#         for task_list in list_timesheet:
#             for task in task_list:
#                 result_list += task

#         for task in result_list:
#             for timesheet_id in task.timesheet_ids:
#                 if self.merge_subtask and timesheet_id.task_id.parent_id:  # if the task has a parent and we merge
#                     parent_task_id = timesheet_id.task_id.parent_id
#                 else:
#                     parent_task_id = timesheet_id.task_id

#                 """task_id = timesheet_id.task_id
#                 parent_task_id = task_id.parent_id or task_id"""

#                 rate_product_id = timesheet_id.so_line.product_id
#                 rate_product_ids |= rate_product_id
#                 time_category_id = timesheet_id.time_category_id
#                 unit_amount = timesheet_id.unit_amount
#                 # project matrix data
#                 project_rate_matrix_key = (project_id, rate_product_id)
#                 project_rate_matrix_data.setdefault(project_rate_matrix_key, 0.)
#                 project_rate_matrix_data[project_rate_matrix_key] += unit_amount
#                 tasks_row_data = projects_row_data.setdefault(project_id, OrderedDict())
#                 # task matrix data
#                 task_rate_matrix_key = (project_id, parent_task_id, rate_product_id)
#                 task_rate_matrix_data.setdefault(task_rate_matrix_key, 0.)
#                 task_rate_matrix_data[task_rate_matrix_key] += unit_amount
#                 time_category_row_data = tasks_row_data.setdefault(parent_task_id, OrderedDict())
#                 # time category matrix data
#                 if detailed:
#                     time_category_matrix_key = (project_id, parent_task_id, time_category_id, rate_product_id)
#                     time_category_rate_matrix_data.setdefault(time_category_matrix_key, 0.)
#                     time_category_rate_matrix_data[time_category_matrix_key] += unit_amount
#                     time_category_row_data.setdefault(time_category_id, None)
                 
#         # ORDRE DES COLONNES DE RATE
#         # reorder rate_product_ids according to the richer one
#         rate_product_ids = rate_product_ids
#         rate_product_ids = product_obj.browse(OrderedSet([
#             couple[1].id for couple in
#             sorted(
#                 [(project_id, rate_product_id)
#                     for project_id in projects_row_data.keys()
#                     for rate_product_id in rate_product_ids],
#                 key=lambda key: project_rate_matrix_data[key],
#                 reverse=True
#             )
#         ]))
#         return {
#             'project_rate_matrix_data': project_rate_matrix_data,
#             'task_rate_matrix_data': task_rate_matrix_data,
#             'time_category_rate_matrix_data': time_category_rate_matrix_data,
#             'rate_product_ids': rate_product_ids,
#             'projects_row_data': projects_row_data,
#         }

    @api.multi
    def _get_aggregated_invoice_report_data(self):
        rate_data, rate_subtotal = self._get_aggregated_invoice_report_rate_data()
        fixed_price_data = self._get_aggregated_invoice_report_fixed_price()
        expenses_and_communication_data = self._get_invoice_report_expenses_and_communication()
        return {
            'rate_data': rate_data,
            'fixed_price_data': fixed_price_data,
            'expenses_and_communication_data': expenses_and_communication_data,
            'rate_subtotal': rate_subtotal,
            '_t': _,
        }

    @api.multi
    def _get_detailed_invoice_report_data(self):
        rate_data, rate_subtotal = self._get_detailed_invoice_report_rate_data()
        fixed_price_data = self._get_detailed_invoice_report_fixed_price()
        expenses_and_communication_data = self._get_invoice_report_expenses_and_communication()
        return {
            'rate_data': rate_data,
            'fixed_price_data': fixed_price_data,
            'expenses_and_communication_data': expenses_and_communication_data,
            'rate_subtotal': rate_subtotal,
            '_t': _,
        }

    @api.multi
    def _get_aggregated_invoice_report_rate_data(self):
        """
        :param self:
        :return: ordered dictionary with the following structure
        {
            section_line_id: {
                rate_line_record : {
                    'qty': qty,
                    'price': price,
                    'currency_id': currency,
                }
            }
        }
        """
        self.ensure_one()
        data = OrderedDict()
        total_not_taxed = 0.
        for timesheet_id in self.timesheet_ids.filtered(lambda t: t.so_line.qty_invoiced)\
                .sorted(lambda t: t.so_line.price_unit, reverse=True):
            rate_sale_line_id = timesheet_id.so_line

            if self.merge_subtask and timesheet_id.task_id.parent_id: #if the task has a parent and we merge
                task_id = timesheet_id.task_id.parent_id
            else:
                task_id = timesheet_id.task_id

            service_sale_line_id = task_id.sale_line_id
            service_section_line_id = service_sale_line_id.section_line_id
            rates_dict = data.setdefault(service_section_line_id, OrderedDict())
            values = rates_dict.setdefault(
                rate_sale_line_id, {
                    'qty': 0.,
                    'price': rate_sale_line_id.price_unit,
                    'currency_id': rate_sale_line_id.currency_id,
                    'uom_id': rate_sale_line_id.product_uom,
                })
            timesheet_uom_id = timesheet_id.product_uom_id
            qty = timesheet_uom_id._compute_quantity(
                timesheet_id.unit_amount_rounded,
                rate_sale_line_id.product_uom
            )
            values['qty'] += qty
            total_not_taxed += qty * values['price']
        # assert abs(total_not_taxed - self.amount_untaxed) < 0.001, _('Something went wrong')
        return data, total_not_taxed

    @api.multi
    def _get_detailed_invoice_report_rate_data(self):
        """
        :param self:
        :return: ordered dictionary with the following structure
        {
            task1_record: {
                rate_line_record : {
                    'qty': qty,
                    'price': price,
                    'currency_id': currency,
                }
            }
        }
        """
        self.ensure_one()
        data = OrderedDict()
        total_not_taxed = 0.
        for timesheet_id in self.timesheet_ids.filtered(lambda t: t.so_line.qty_invoiced)\
                .sorted(lambda t: t.so_line.price_unit, reverse=True):
            rate_sale_line_id = timesheet_id.so_line

            if self.merge_subtask and timesheet_id.task_id.parent_id: #if the task has a parent and we merge
                task_id = timesheet_id.task_id.parent_id
            else:
                task_id = timesheet_id.task_id

            rates_dict = data.setdefault(task_id, OrderedDict())
            values = rates_dict.setdefault(
                rate_sale_line_id, {
                    'qty': 0.,
                    'price': rate_sale_line_id.price_unit,
                    'currency_id': rate_sale_line_id.currency_id,
                    'uom_id': rate_sale_line_id.product_uom,
                })
            timesheet_uom_id = timesheet_id.product_uom_id
            qty = timesheet_uom_id._compute_quantity(
                timesheet_id.unit_amount_rounded,
                rate_sale_line_id.product_uom
            )
            values['qty'] += qty
            total_not_taxed += qty * values['price']
        # assert abs(total_not_taxed - self.amount_untaxed) < 0.001, _('Something went wrong')
        return data, total_not_taxed

    @api.multi
    def _get_detailed_invoice_report_fixed_price(self):
        """
        :param self:
        :return: ordered dictionary with the following structure
        {
            service_line_record : {
                'subtotal': subtotal,
                'currency_id': currency,
            }
        }
        """
        self.ensure_one()
        fixed_price_data = OrderedDict()
        for line in self.invoice_line_ids:
            if line.product_id.vcls_type != 'vcls_service':
                continue
            fixed_price_data.setdefault(line, {
                'subtotal': line.price_subtotal,
                'currency_id': line.currency_id,
            })
        for key in list(fixed_price_data):
            value = fixed_price_data[key]
            if not value['subtotal']:
                del fixed_price_data[key]
        return fixed_price_data

    @api.multi
    def _get_invoice_report_expenses_and_communication(self):
        """
        :param self:
        :return: ordered dictionary with the following structure
        {
            product_category_record : {
                'subtotal': subtotal,
                'currency_id': currency,
            }
        }
        """
        self.ensure_one()
        data = OrderedDict()
        for line in self.invoice_line_ids:
            if line.product_id.vcls_type not in ('expense', 'communication'):
                continue
            value = data.setdefault(line.product_id.categ_id, {
                'subtotal': 0.,
                'currency_id': line.currency_id,
            })
            value['subtotal'] += line.price_subtotal
        for key in list(data):
            value = data[key]
            if not value['subtotal']:
                del data[key]
        return data

    @api.multi
    def _get_aggregated_invoice_report_fixed_price(self):
        """
        :param self:
        :return: ordered dictionary with the following structure
        {
            service_section_line_record : {
                'subtotal': subtotal,
                'currency_id': currency,
            }
        }
        """
        self.ensure_one()
        fixed_price_data = OrderedDict()
        for line in self.invoice_line_ids:
            if line.product_id.vcls_type != 'vcls_service':
                continue
            section_line_id = line.section_line_id
            value = fixed_price_data.setdefault(section_line_id, {
                'subtotal': 0.,
                'currency_id': line.currency_id,
            })
            value['subtotal'] += line.price_subtotal
        for key in list(fixed_price_data):
            value = fixed_price_data[key]
            if not value['subtotal']:
                del fixed_price_data[key]
        return fixed_price_data

    def get_communication_amount(self):
        total_amount = 0
        lines = self.invoice_line_ids
        #_logger.info("Invoice Lines {}".format(len(lines)))
        for line in lines:
            product = line.product_id
            #_logger.info("Product {} elligible {}".format(product.name, product.communication_elligible))
            if product:
                if product.id != self.env.ref('vcls-invoicing.product_communication_rate').id:
                    if product.communication_elligible:
                        total_amount += line.price_subtotal
                        #_logger.info("Communication Elligible {}".format(product.name))
                else:
                    # We suppress the communication rate line if already existingin order to replace and recompute it
                    _logger.info("COM UNLINK")
                    line.unlink()
            else:
                total_amount += line.price_subtotal
        return total_amount

    @api.multi
    def action_ready_for_approval(self):

        if self.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if self.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        if self.filtered(lambda inv: not inv.account_id):
            raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))

        for invoice in self:
            invoice.write({'ready_for_approval': True})
            #and we send a scheduled action to the AM and the LC's
            activity_type = self.env['mail.activity.type'].search([('name','=','Invoice Review')],limit=1)
            if activity_type:
                users_to_notify = self.env['res.users']
                users_to_notify |= invoice.commercial_partner_id.user_id
                #we also notify the LM of the invoice admin
                connected_employee = self.env['hr.employee'].search([('user_id','=',invoice.user_id.id)],limit=1)
                if connected_employee:
                    users_to_notify |= connected_employee.parent_id.user_id
                #we add the LC's
                users_to_notify |= invoice.project_ids.mapped('user_id')
                #users_to_notify 
                for user in users_to_notify:
                    self.env['mail.activity'].create({
                    'res_id': invoice.id,
                    'res_model_id': self.env.ref('account.model_account_invoice').id,
                    'activity_type_id': activity_type.id,
                    'user_id': user.id,
                    'summary': _('Please review the invoice PDF for {}.').format(
                        invoice.name),
                    })

    @api.model
    def create(self, vals):
        invoice = super(Invoice, self).create(vals)
        invoice._onchange_partner_id()
        _logger.info("INVOICE CREATE ID {} VALS {}".format(invoice.id, vals))
        invoice._message_subscribe_account_payable()
        return invoice

    def _message_subscribe_account_payable(self):
        # subscribe accountant contact contact
        account_payable_partner = self.env.ref(
            'vcls-invoicing.res_partner_vcls_account_payable',
            raise_if_not_found=False
        )
        if account_payable_partner:
            for invoice in self:
                invoice._message_subscribe(partner_ids=[account_payable_partner.id])

    def _message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, customer_ids=None):
        # Add accountant contact to subscribed partners, in order to keep them up to date
        account_payable_partner = self.env.ref(
            'vcls-invoicing.res_partner_vcls_account_payable',
            raise_if_not_found=False
        )
        if account_payable_partner and account_payable_partner.id not in partner_ids:
            if not partner_ids:
                partner_ids = []
            partner_ids += [account_payable_partner.id]
        return super(Invoice, self)._message_subscribe(
            partner_ids, channel_ids,
            subtype_ids, customer_ids
        )

   

    @api.multi
    def write(self, vals):
       
        if self._context.get('create_communication'):
            self._message_subscribe_account_payable()
            return super(Invoice, self).write(vals)
        ret = False
        _logger.info("INVOICE WRITE IDS {} VALS {}".format(self.ids,vals))
        for inv in self:
            self = self.with_context(force_company=inv.company_id.id,company_id=inv.company_id.id)
            inv = inv.with_context(force_company=inv.company_id.id,company_id=inv.company_id.id)
            inv._message_subscribe_account_payable()

            if vals.get('sent'):
                vals.update({'invoice_sending_date': fields.Datetime.now()})

            if not self.env.context.get('source_data'):
                vals = inv.with_context(source_data=True)._get_source_data(vals)

            #call parent
            ret = super(Invoice, inv).write(vals)

            #release timesheets if any
            if inv.state == 'cancel':
                if inv.timesheet_ids:
                    for timesheet in inv.timesheet_ids:
                        timesheet.stage_id = 'invoiceable'
            
            #communication rate
            if inv.communication_rate > 0 and not self.env.context.get('communication_rate') and vals.get('state',inv.state)=='draft':
                total_amount = inv.get_communication_amount()
                if total_amount:
                    invoice_line_obj = self.env['account.invoice.line']
                    line_cache = invoice_line_obj.new()
                    line_cache.invoice_id = inv.id
                    line_cache.account_analytic_id = inv.parent_analytic_account_id.id
                    line_cache.product_id = self.env.ref('vcls-invoicing.product_communication_rate').id
                    line_cache._onchange_product_id()
                    line_cache.price_unit = total_amount * inv.communication_rate
                    line_cache.name = "Communication ({}%)".format(100 * inv.communication_rate)
                    line_cache.quantity = 1
                    line_values = line_cache._convert_to_write({
                        name: line_cache[name]
                        for name in line_cache._cache
                    })
                    invoice_line_obj.with_context(create_communication=True)\
                        .create(line_values)
                    #_logger.info("COM RATE LINE {}".format(line_values))
        return ret

    @api.depends('payment_term_id', 'invoice_sending_date')
    def _compute_vcls_due_date(self):
        for rec in self:
            if rec.payment_term_id and rec.invoice_sending_date:
                pterm = rec.payment_term_id
                pterm_list = \
                    pterm.with_context(currency_id=rec.company_id.currency_id.id).compute(value=1,
                                                                                          date_ref=date.today())[0]
                rec.vcls_due_date = max(line[0] for line in pterm_list)

    @api.multi
    def unlink(self):
        orders = self.env['sale.order']
        for invoice in self:
            if invoice.timesheet_ids:
                invoice.timesheet_ids.write({'stage_id':'invoiceable'})
                orders |= invoice.timesheet_ids.mapped('so_line.order_id')       
            ret = super(Invoice, invoice).unlink()
            
        orders.mapped('order_line')._compute_qty_delivered()
        return ret

    @api.multi
    def html_to_string(self, html_format):
        self.ensure_one()
        return lxml.html.document_fromstring(html_format).text_content()


    def get_analytic_accounts_lines(self):
        so_names = self.origin.split(', ')
        line_ids = self.env['sale.order'].sudo().search([('name', 'in', so_names)]).mapped(
            'analytic_account_id.line_ids')
        categs = {}
        supplier_expenses = self.invoice_line_ids.filtered(lambda il: il.product_id.purchase_ok)
        communications_expenses = self.invoice_line_ids.filtered(lambda il: il.product_id.id != self.env.ref(
            'vcls-invoicing.product_communication_rate').id and il.product_id.communication_elligible)
        if supplier_expenses:
            categs.update({'supplier_expenses': supplier_expenses})
        if communications_expenses:
            categs.update({'communications_expenses': communications_expenses})
        for categ_id, same_product_categ in groupby(line_ids, key=lambda al: al.product_id.categ_id):
            same_product_cat = list(same_product_categ)
            categ_name = categ_id.name
            categ_amount = sum(p.amount for p in same_product_cat)
            categs.update({categ_name: categ_amount})
        return categs

    def deliverable_grouped_lines(self):
        sale_line_ids = self.invoice_line_ids.mapped('sale_line_ids').filtered(
            lambda sol: not sol.product_id.recurring_invoice)
        deliverable_groups = {}
        deliverable_lines = []
        for deliverable_id, same_deliverable in groupby(sale_line_ids, key=lambda sol: sol.product_id.deliverable_id):
            deliverable_name = deliverable_id.name
            if deliverable_name:
                deliverable_lines += [line for line in same_deliverable]
                deliverable_groups[deliverable_name] = deliverable_lines
        return deliverable_groups

    @api.multi
    def _create_activity_attachment(self, report_template, report_name):
        self.ensure_one()
        attachment_obj = self.env['ir.attachment']
        data = report_template.render_qweb_pdf(self.ids)
        name = self._get_invoice_report_filename(report_name)
        values = {
            'name': name,
            'datas': base64.b64encode(data[0]),
            'datas_fname': name,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        }
        attachment_id = attachment_obj.create(values)
        if self._context.get('_get_attachment_id'):
            return attachment_id
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/web/content/%s/%s?download=true' % (attachment_id.id, name)
        }

    @api.multi
    def _get_invoice_report_filename(self, report_name):
        self.ensure_one()
        project_string = ''
        for project in self.project_ids:
            project_string += project.name.split('|')[0]

        count_attachments = self.env['ir.attachment'].search_count([('res_model', '=', self._name),
                                                                    ('res_id', '=', self.id),
                                                                    ('name', 'like', report_name)]) + 1
        return (self.timesheet_limit_date and self.timesheet_limit_date.strftime('%Y-%m-%d') or '') \
            + project_string + report_name + '_V' + str(count_attachments)

    @api.multi
    def generate_report(self, report_template, report_name, message):
        self.ensure_one()
        if not self.timesheet_ids and report_name==ACTIVITYREPORT:
            raise UserError(_('There is no timesheet associated with the invoice: %s') % self.name)
        if not report_template:
            raise ValidationError(_(message))
        # create attachment
        attachment =  self._create_activity_attachment(report_template, report_name)
        self._compute_attachment_count()
        return attachment

    @api.multi
    def action_generate_draft_invoice(self):
        self.ensure_one()
        return self.generate_report(self.invoice_template, DRAFTINVOICE, _("You need to select an invoice template"))

    @api.multi
    def action_generate_activity_report(self):
        self.ensure_one()
        return self.generate_report(self.activity_report_template,
                                    ACTIVITYREPORT, _("You need to select an activity report template"))

    @api.multi
    def action_invoice_sent(self):
        """
        Override of action_invoice_sent to attach the invoice_template
        """
        if not self.invoice_template:
            raise ValidationError(_('Please set an Invoice Template before'))
        res = super(Invoice, self).action_invoice_sent()
        attachment_id = self.with_context(_get_attachment_id=True)._create_activity_attachment(self.invoice_template,
                                                                                               self._get_invoice_report_filename(DRAFTINVOICE))
        res['context'].update({'default_attachment_ids': attachment_id.ids})
        return res

    @api.multi
    def action_activity_report_attachments(self):
        action = self.env.ref('vcls-invoicing.action_invoice_attachment').read()[0]
        action['domain'] = [('res_id', '=', self.id),('name', 'like', ACTIVITYREPORT)]
        return action

    @api.multi
    def action_generate_draft_invoice_attachments(self):
        action = self.env.ref('vcls-invoicing.action_invoice_attachment').read()[0]
        action['domain'] = [('res_id', '=', self.id), ('name', 'like', DRAFTINVOICE)]
        return action

