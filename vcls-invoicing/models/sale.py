# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

from lxml import etree
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    risk_ids = fields.Many2many('risk', string='Risk')

    risk_score = fields.Integer(
        string='Risk Score',
        compute = '_compute_risk_score',
    )

    po_id = fields.Many2one('invoicing.po', string ='Purchase Order')

    invoicing_frequency = fields.Selection([
        ('month','Month'),
        ('trimester','Trimester'),
        ('milestone','Milestone')],
        default =lambda self: self.partner_id.invoicing_frequency,
    )
    timesheet_limit_date = fields.Date(compute='compute_timesheet_limite_date', inverse='inverse_timesheet_limite_date', store=True,)
    invoice_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'account.invoice')])
    activity_report_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'account.analytic.line'),
                                                                            ('report_name', '=', 'activity_report')])
    communication_rate = fields.Selection([('0.0', '0%'),
                                           ('0.005', '0.5%'),
                                           ('0.01', '1%'),
                                           ('0.015', '1.5%'),
                                           ('0.02', '2%'),
                                           ('0.025', '2.5%'),
                                           ('0.03', '3%'),
                                           ], 'Communication Rate', default='0.0')
    financial_config_readonly = fields.Boolean(compute='compute_financial_config_readonly')

    @api.depends('partner_id.risk_ids')
    def _compute_risk_ids(self):
        resourceSo ="sale.order,{}".format(self.id)
        risk_ids = self.env['risk'].search([('resource','=',resourceSo)])
        if self.partner_id:
            resourcePrtn ="res.partner,{}".format(self.partner_id.id)
            risk_ids |= self.env['risk'].search([('resource','=',resourcePrtn)])
        if risk_ids:
            self.risk_ids |= risk_ids

    @api.one
    @api.depends('partner_id.invoice_ids', 'partner_id.invoice_ids.state',
                 'invoicing_frequency')
    def compute_timesheet_limite_date(self):
        customer_last_invoice = sorted(
            self.partner_id.invoice_ids.filtered(lambda inv: inv.invoice_sending_date and inv.state != 'cancel')
            , key=lambda inv: inv.invoice_sending_date, reverse=True)
        if customer_last_invoice and customer_last_invoice[0].timesheet_limit_date and\
                self.invoicing_frequency and self.invoicing_frequency != 'milestone':
            if self.invoicing_frequency == 'month':
                new_date = (customer_last_invoice[0].timesheet_limit_date + relativedelta(day=1,
                                                                                          months=2)) - relativedelta(
                    day=1)
            if self.invoicing_frequency == 'trimester':
                new_date = (customer_last_invoice[0].timesheet_limit_date + relativedelta(day=1,
                                                                                          months=4)) - relativedelta(
                    day=1)
            self.timesheet_limit_date = new_date

    def inverse_timesheet_limite_date(self):
        return

    @api.one
    @api.depends('project_id.user_id','partner_id.invoice_admin_id', 'parent_id')
    def compute_financial_config_readonly(self):
        self.financial_config_readonly =((self.project_id.user_id == self.env.user) or\
                                        (self.partner_id.invoice_admin_id == self.env.user)) and not self.parent_id

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
        try:
            risk_company = self.env.ref('vcls-invoicing.non_standard_company')
            risk_rate = self.env.ref('vcls-invoicing.non_standard_rates')
        except:
            risk_company = False
            risk_rate = False

        for so in self:

            resource ="sale.order,{}".format(so.id)

            if so.company_id:
                if so.company_id != self.env.ref('vcls-hr.company_VCFR'):
                    existing = self.env['risk'].search([('resource', '=', resource),('risk_type_id','=',risk_company.id)])
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

    def _compute_risk_score(self):
        for so in self:
            so.risk_score = sum(so.risk_ids.mapped('score'))
                    
            

        """order_lines = self.order_line
        
        for line in order_lines:
            so_line_price = line.price_unit
            product_prices = line.product_id.item_ids

            try:
                if line.product_id.seniority_level_id:
                    for product_price in product_prices:
                        if product_price.pricelist_id == line.pricelist_id and product_price.fixed_price != so_line_price:
                            risk_type = self.env.ref('vcls-invoicing.non_standard_rates')
                            resource ='sale.order,' + str(self.id)
                            risk = self.env['risk'].search([('resource', '=', resource)])
                            if not risk:
                                risk = self.env['risk']._raise_risk(risk_type, resource).id
                                self.risk_ids = risk

                if self.company_id.id != self.env.ref('vcls-hr.company_VCFR').id:
                    risk_type = self.env.ref('vcls-invoicing.non_standard_company')
                    resource ='sale.order,' + str(self.id)
                    risk = self.env['risk'].search([('resource', '=', resource)])
                    if not risk:
                        risk = self.env['risk']._raise_risk(risk_type, resource).id
                        self.risk_ids = risk

            except Exception:
                pass"""
    
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
