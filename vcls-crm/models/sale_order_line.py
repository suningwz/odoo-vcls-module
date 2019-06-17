# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    #Override the default ordered quantity to be 0 when we order rates items
    product_uom_qty = fields.Float(
        default = 0,
        )
    
    @api.onchange('product_id')
    def _onchange_product(self):
        for line in self:
            if line.product_id.seniority_level_id: #if there's a seniority level defined, it means this is a rate
                line.product_uom_qty = 0
    
    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.product_id.seniority_level_id: #if there's a seniority level defined, it means this is a rate
                line.product_uom_qty = 0

        return lines

    def _timesheet_create_project(self):
        project = super(SaleOrderLine, self)._timesheet_create_project()
        project.update({'project_type': 'client'})
        return project
    

    