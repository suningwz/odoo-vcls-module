from odoo import api, fields, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    group_invoice_method = fields.Selection([('one', 'Only this order'),
                                             ('project', 'project'),
                                             ('program', 'program'),
                                             ('agreement', 'agreement'),],string='Grouping Invoice by', default='one')
    
    @api.multi
    def create_invoices(self):
        context = self._context

        if self.group_invoice_method == 'project':
            projects = self.env['sale.order'].browse(self._context.get('active_ids', [])).mapped('project_ids')
            sale_orders = self.env['sale.order.line'].search([('project_id', 'in', projects.ids)]).mapped('order_id')
            context['active_ids'] = sale_orders.ids
        elif self.group_invoice_method == 'program':
            programs = self.env['sale.order'].browse(self._context.get('active_ids', [])).mapped('program_id')
            sale_orders = self.env['sale.order'].search([('program_id', 'in', programs.ids)])
            context['active_ids'] = sale_orders.ids
        elif self.group_invoice_method == 'agreement':
            agreements = self.env['sale.order'].browse(self._context.get('active_ids', [])).mapped('agreement_id')
            sale_orders = self.env['sale.order'].search([('agreement_id', 'in', agreements.ids)])
            context['active_ids'] = sale_orders.ids

        return super(SaleAdvancePaymentInv, self.with_context(context)).create_invoices()
