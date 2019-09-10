from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

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

    def _timesheet_create_task_prepare_values(self, project):
        task_vals = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        task_vals.update(completion_elligible=self.product_id.completion_elligible)
        return task_vals
