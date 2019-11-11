# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

from lxml import etree
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def get_activity_report_template(self):
        order_id = self._context.get('params', {}).get('id')
        if order_id:
            order_id = self.env['sale.order'].browse(order_id)
            return order_id.partner_id.activity_report_template
        return False

    risk_ids = fields.Many2many('risk', string='Risk')

    risk_score = fields.Integer(
        string='Risk Score',
        compute = '_compute_risk_score',
        store = True,
    )

    po_id = fields.Many2one('invoicing.po', string ='Purchase Order')

    invoicing_frequency = fields.Selection([
        ('month', 'Month'),
        ('trimester', 'Trimester'),
        ('milestone', 'Milestone')],
        default =lambda self: self.partner_id.invoicing_frequency,
    )
    
    timesheet_limit_date = fields.Date(
        compute='_compute_timesheet_limit_date',
        inverse='_inverse_timesheet_limit_date',
        store=True
    )
    invoice_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'account.invoice')])
    activity_report_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'activity.report.groupment')])
    #activity_report_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'account.analytic.line'),
    #                                                                        ('report_name', '=', 'activity_report')])
    communication_rate = fields.Selection([
        ('0.0', '0%'),
        ('0.005', '0.5%'),
        ('0.01', '1%'),
        ('0.015', '1.5%'),
        ('0.02', '2%'),
        ('0.025', '2.5%'),
        ('0.03', '3%'),
    ], 'Communication Rate', default='0.0')
    financial_config_readonly = fields.Boolean(
        compute='compute_financial_config_readonly',
        store=False,
        )

    activity_report_template = fields.Many2one(
        'ir.actions.report',
        default=lambda self: self.get_activity_report_template()
    )

    invoiceable_amount = fields.Monetary(
        compute="_compute_invoiceable_amount",
        store=True,
    )

    @api.depends('order_line','order_line.untaxed_amount_to_invoice')
    def _compute_invoiceable_amount(self):
        for so in self:
            so.invoiceable_amount = sum(so.order_line.mapped('untaxed_amount_to_invoice'))

    @api.depends('partner_id.risk_ids')
    def _compute_risk_ids(self):
        resourceSo = "sale.order,{}".format(self.id)
        risk_ids = self.env['risk'].search([('resource', '=', resourceSo)])
        if self.partner_id:
            resourcePrtn = "res.partner,{}".format(self.partner_id.id)
            risk_ids |= self.env['risk'].search([('resource', '=', resourcePrtn)])
        if risk_ids:
            self.risk_ids |= risk_ids

    @api.one
    @api.depends('partner_id.invoice_ids', 'partner_id.invoice_ids.state',
                 'invoicing_frequency')
    def _compute_timesheet_limit_date(self):
        customer_last_invoice = sorted(
            self.invoice_ids.filtered(
                lambda inv: inv.invoice_sending_date and inv.state != 'cancel'
            ), key=lambda inv: inv.invoice_sending_date, reverse=True
        )
        customer_last_invoice = customer_last_invoice and customer_last_invoice[0] or None
        if customer_last_invoice and customer_last_invoice.timesheet_limit_date and \
                self.invoicing_frequency and self.invoicing_frequency != 'milestone':
            if self.invoicing_frequency == 'month':
                new_date = customer_last_invoice.timesheet_limit_date +\
                           relativedelta(day=1, months=2) -\
                           relativedelta(day=1)
            if self.invoicing_frequency == 'trimester':
                new_date = customer_last_invoice.timesheet_limit_date +\
                           relativedelta(day=1, months=4) -\
                           relativedelta(day=1)
            self.timesheet_limit_date = new_date

    def _inverse_timesheet_limit_date(self):
        pass

    @api.one
    @api.depends('project_id.user_id','partner_id.invoice_admin_id', 'parent_id')
    def compute_financial_config_readonly(self):
        self.financial_config_readonly =((self.project_id.user_id == self.env.user) or\
                                        (self.partner_id.invoice_admin_id == self.env.user) or\
                                        (self.env.user.has_group('vcls_security.group_project_controller'))) and not self.parent_id

    def action_risk(self):
        view_ids = [self.env.ref('vcls-risk.view_risk_tree').id,
                    self.env.ref('vcls-risk.view_risk_kanban').id, 
                    self.env.ref('vcls-risk.view_risk_form').id ]

        return {
            'name': 'All Risks',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form',
            'view_ids': view_ids,
            'target': 'current',
            'res_model': 'risk',
            'type': 'ir.actions.act_window',
            'context': {'search_default_id':self.risk_ids.ids,},
        } 

    def check_risk(self):
        risk_company = self.env.ref('vcls-invoicing.non_standard_company', raise_if_not_found=False) or False
        risk_rate = self.env.ref('vcls-invoicing.non_standard_rates', raise_if_not_found=False) or False

        for so in self:

            resource = "sale.order,{}".format(so.id)

            if so.company_id:
                if so.company_id != self.env.ref('vcls-hr.company_VCFR'):
                    existing = self.env['risk'].search([
                        ('resource', '=', resource),
                        ('risk_type_id', '=', risk_company.id)
                    ])
                    if not existing:
                        so.risk_ids |= self.env['risk']._raise_risk(risk_company, resource)
            
            rates = so.order_line.filtered(lambda r: r.product_id.seniority_level_id)

            for rate in rates:
                std_price = rate.product_id.item_ids.filtered(lambda s: s.pricelist_id == so.pricelist_id)
                if std_price:
                    if rate.price_unit < std_price[0].fixed_price:
                        existing = self.env['risk'].search([('resource', '=', resource),('risk_type_id','=',risk_rate.id)])
                        if not existing:
                            so.risk_ids |= self.env['risk']._raise_risk(risk_rate, resource)
                        break
    
    @api.depends('so.risk_ids','so.risk_ids.score')
    def _compute_risk_score(self):
        for so in self:
            so.risk_score = sum(so.risk_ids.mapped('score'))

    @api.multi
    def write(self, vals):
        for rec in self:
            childs = vals.get('child_ids', False) or rec.child_ids
            if childs:
                params = ('invoicing_frequency', 'invoice_template', 'activity_report_template', 'communication_rate'
                          , 'pricelist_id')
                keys = ('invoicing_frequency', 'invoice_template', 'activity_report_template', 'communication_rate'
                        , 'pricelist_id')
                values = [vals.get(key) for key in params]
                dict_values = {keys[i]: values[i] for i in range(0, len(values)) if values[i]}
                if len(dict_values):
                        for child in childs:
                            super(SaleOrder, child).write(dict_values)
                            child.check_risk()
        result = super(SaleOrder, self).write(vals)
        self.check_risk()
        return result

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        result.check_risk()
        return result

    @api.onchange('partner_id')
    def get_partner_financial_config(self):
        self.invoicing_frequency = self.partner_id.invoicing_frequency
        self.invoice_template = self.partner_id.invoice_template
        self.activity_report_template = self.partner_id.activity_report_template
        self.communication_rate = self.partner_id.communication_rate
        self.pricelist_id = self.partner_id.property_product_pricelist
