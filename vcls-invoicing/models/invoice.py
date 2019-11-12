# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import lxml
from itertools import groupby
from datetime import date

from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


import logging
_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    _inherit = 'account.invoice'

    def _get_default_po_id(self):
        return self.env['sale.order'].search([('invoice_ids', 'in', [self.id])], limit=1).po_id

    po_id = fields.Many2one('invoicing.po', 
                            default = _get_default_po_id,  
                            string ='Purchase Order')

    user_id = fields.Many2one(
        'res.users',
        string='Invoicing Administrator',
        )

    invoice_sending_date = fields.Datetime()
    parent_quotation_timesheet_limite_date = fields.Date(
        string='Parent Timesheet Limit Date',
        compute='compute_parent_quotation_timesheet_limite_date'
    )
    vcls_due_date = fields.Date(string='Custom Due Date', compute='_compute_vcls_due_date')
    origin_sale_orders = fields.Char(compute='compute_origin_sale_orders',string='Origin')

    ready_for_approval = fields.Boolean(default=False)

    invoice_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'account.invoice')])
    activity_report_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'activity.report.groupment')])

    def get_communication_amount(self):
        total_amount = 0
        lines = self.invoice_line_ids
        _logger.info("Invoice Lines {}".format(len(lines)))
        for line in lines:
            product = line.product_id
            _logger.info("Product {} elligible {}".format(product.name, product.communication_elligible))
            if product:
                if product.id != self.env.ref('vcls-invoicing.product_communication_rate').id:
                    if product.communication_elligible:
                        total_amount += line.price_subtotal
                        _logger.info("Communication Elligible {}".format(product.name))
                else:
                    # We suppress the communication rate line if already existingin order to replace and recompute it
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
            
    @api.model
    def create(self, vals):
        ret = super(Invoice, self).create(vals)       
        partner = ret.partner_id
        if ret.partner_id.invoice_admin_id:
            ret.user_id = ret.partner_id.invoice_admin_id
        if partner.communication_rate:
            _logger.info("COM RATE {}".format(partner.communication_rate))
            try:
                total_amount = ret.get_communication_amount()
            except:
                total_amount = False
            if total_amount:
                line = self.env['account.invoice.line'].new()
                line.invoice_id = ret.id
                line.product_id = self.env.ref('vcls-invoicing.product_communication_rate').id
                line._onchange_product_id()
                line.price_unit = total_amount * partner.communication_rate / 100
                line.quantity = 1
                ret.with_context(communication_rate=True).invoice_line_ids += line
        return ret
    
    @api.multi
    def write(self, vals):
        if vals.get('sent'):
            vals.update({'invoice_sending_date': fields.Datetime.now()})
        ret = super(Invoice, self).write(vals)
        for rec in self:
            partner = rec.partner_id
            if partner.communication_rate and not self.env.context.get('communication_rate'):
                try:
                    total_amount = ret.get_communication_amount()
                except:
                    total_amount = False
                if total_amount:
                    line = self.env['account.invoice.line'].new()
                    line.invoice_id = rec.id
                    line.product_id = self.env.ref('vcls-invoicing.product_communication_rate').id
                    line._onchange_product_id()
                    line.price_unit = total_amount * partner.communication_rate / 100
                    line.quantity = 1
                    rec.with_context(communication_rate=True).invoice_line_ids += line
            if rec.state == 'cancel':
                if self.timesheet_ids:
                    for timesheet in self.timesheet_ids:
                        timesheet.stage_id = 'invoiceable'
        return ret
    
    
    def action_print_activity_report(self):
        ctx = self._context.copy()
        if not self.timesheet_ids:
            raise UserError(_('There is no timesheet associated with the invoice: %s') % self.name)
        ctx.update(default_invoice_id=self.id, invoice_id=self.id)
        activity_form_id = self.env.ref('vcls-invoicing.activity_report_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_model': 'activity.report.groupment',
            'views': [(activity_form_id, 'form')],
            'view_id': activity_form_id,
            'context': ctx,
        }

    @api.depends('invoice_line_ids')
    def compute_parent_quotation_timesheet_limite_date(self):
        for invoice in self:
            so_with_timesheet_limit_date = invoice._get_parents_quotations().filtered(
                lambda so: so.timesheet_limit_date)
            if so_with_timesheet_limit_date:
                invoice.parent_quotation_timesheet_limite_date = so_with_timesheet_limit_date[0].timesheet_limit_date

    def _get_parents_quotations(self):
        return self.mapped('invoice_line_ids.sale_line_ids.order_id')

    @api.depends('payment_term_id', 'invoice_sending_date')
    def _compute_vcls_due_date(self):
        for rec in self:
            if rec.payment_term_id and rec.invoice_sending_date:
                pterm = rec.payment_term_id
                pterm_list = \
                    pterm.with_context(currency_id=rec.company_id.currency_id.id).compute(value=1,
                                                                                          date_ref=date.today())[0]
                rec.vcls_due_date = max(line[0] for line in pterm_list)

    @api.depends('invoice_line_ids')
    def compute_origin_sale_orders(self):
        for rec in self:
            sale_orders = rec._get_parents_quotations()
            rec.origin_sale_orders = ','.join(sale_orders.mapped('name'))

    @api.multi
    def unlink(self):
        if self.timesheet_ids:
            for timesheet in self.timesheet_ids:
                timesheet.stage_id = 'invoiceable'
        return super(Invoice, self).unlink()

    @api.multi
    def html_to_string(self, html_format):
        self.ensure_one()
        return lxml.html.document_fromstring(html_format).text_content()

    """
    def parent_quotation_informations(self):

        if not self.origin:
            return []
        names = self.origin.split(', ')
        customer_precedent_invoice = ""
        quotation = self.env['sale.order'].search([('name', 'in', names)], limit=1)
        if not quotation:
            return []
        parent_order = quotation.parent_id or quotation
        while parent_order.parent_id:
            parent_order = parent_order.parent_id
        
        if self.timesheet_limit_date:
            customer_precedent_invoices = parent_order.partner_id.invoice_ids.filtered(
                lambda i: i.id != self.id and i.timesheet_limit_date < self.timesheet_limit_date).sorted(
                key=lambda v: v['timesheet_limit_date'], reverse=True)
            customer_precedent_invoice = customer_precedent_invoices and\
                customer_precedent_invoice[0].timesheet_limit_date.strftime("%d/%m/%Y")
        
        return [
            ('name', parent_order.name),
            ('scope_work', self.html_to_string(parent_order.scope_of_work) or ''),
            ('po_id', parent_order.po_id.name or ''),
            ('From', customer_precedent_invoice or ''),
            ('To', self.timesheet_limit_date and self.timesheet_limit_date.strftime("%d/%m/%Y") or '')
        ]
    """
    def parent_quotation_informations(self):

        if not self.origin:
            return []
        names = self.origin.split(', ')
        customer_precedent_invoice = ""
        quotation = self.env['sale.order'].search([('name', 'in', names)], limit=1)
        if not quotation:
            return []
        parent_order = quotation.parent_id or quotation
        while parent_order.parent_id:
            parent_order = parent_order.parent_id
        
        
        
        return [
            ('name', parent_order.name),
            ('scope_work', self.html_to_string(parent_order.scope_of_work) or ''),
            ('po_id', parent_order.po_id.name or ''),
            ('From', self.timesheet_limit_date and self.timesheet_limit_date.strftime("%d/%m/%Y") or ''),
            ('To', self.timesheet_limit_date and self.timesheet_limit_date.strftime("%d/%m/%Y") or '')
        ]

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


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    vcls_type = fields.Char(compute='linked_product_type', store=True)

    @api.multi
    @api.depends('product_id')
    def linked_product_type(self):
        for rec in self:
            if rec.product_id.type == 'service' and rec.product_id.service_policy == 'delivered_timesheet' and \
                    rec.product_id.service_tracking in ('no', 'project_only'):
                rec.vcls_type = 'rates'
            elif rec.product_id.type == 'service' and rec.product_id.service_policy == 'delivered_manual' and \
                    rec.product_id.service_tracking == 'task_new_project' and \
                    not any(l.product_id.seniority_level_id for l in rec.invoice_id.invoice_line_ids):
                rec.vcls_type = 'fixed'
            elif rec.product_id.type == 'service' and rec.product_id.service_policy == 'delivered_manual' and \
                    rec.product_id.service_tracking == 'task_new_project' and \
                    rec.invoice_id.invoice_line_ids.filtered(lambda r: r.product_id.seniority_level_id):
                rec.vcls_type = 'tm'
