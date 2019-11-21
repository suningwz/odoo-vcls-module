from odoo import api, fields, models, _
from itertools import groupby

import logging
_logger = logging.getLogger(__name__)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    group_invoice_method = fields.Selection([
        #('one', 'Only this order'),
        ('project', 'Project and Extensions'),
        ('program', 'Program'),
        #('agreement', 'agreement'),
        ],
        string='Grouping Invoice by', default='project')
    
    @api.multi
    def create_invoices(self):
        context = self._context.copy()

        active_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        related_orders = active_orders
        pos = self.env['invoicing.po']

        if self.group_invoice_method == 'project':
            for order in active_orders:
                related_orders |= order.parent_id | order.parent_sale_order_id | order.child_ids
                pos |=  order.po_id | order.parent_id.po_id | order.parent_sale_order_id.po_id | order.child_ids.po_ids

        _logger.info(" Found orders {} and POs {}".format(related_orders.mapped('name'),pos.mapped('name')))

        """if self.group_invoice_method == 'project':
            projects = self.env['sale.order'].browse(self._context.get('active_ids', [])).mapped('project_ids')
            for project in projects:
                projects_to_invoice_ids = [p.id for p in self.get_projects(project)]
            sale_orders = self.env['sale.order.line'].search([('project_id', 'in', projects_to_invoice_ids)]).mapped('order_id')
            sale_orders = sale_orders.filtered(lambda t: t.po_id)
            for po_id, same_po_orders in groupby(sale_orders, key=lambda so: so.po_id):
                same_po_orders_ids = list(same_po_orders)
                po_orders_to_invoice_ids = [p.id for p in same_po_orders_ids]
                context['active_ids'] = po_orders_to_invoice_ids
                return super(SaleAdvancePaymentInv, self.with_context(context)).create_invoices()
        elif self.group_invoice_method == 'program':
            programs = self.env['sale.order'].browse(self._context.get('active_ids', [])).mapped('program_id')
            sale_orders = self.env['sale.order'].search([('program_id', 'in', programs.ids)])
            context['active_ids'] = sale_orders.ids
        elif self.group_invoice_method == 'agreement':
            agreements = self.env['sale.order'].browse(self._context.get('active_ids', [])).mapped('agreement_id')
            sale_orders = self.env['sale.order'].search([('agreement_id', 'in', agreements.ids)])
            context['active_ids'] = sale_orders.ids"""

        return super(SaleAdvancePaymentInv, self.with_context(context)).create_invoices()

    @api.model
    def _get_children(self, project, children=[]):
        children += project
        for child in project.child_id:
            children += child
            self._get_children(child, children)
        return children

    def get_projects(self,project_id):
        parent_project = project_id.parent_id or project_id
        while parent_project.parent_id:
            parent_project = parent_project.parent_id
        projects = list(set(self._get_children(parent_project)))
        return projects
