from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    forecasted_amount = fields.Monetary(
        compute = "_compute_forecasted_amount",
        store = True,
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

    def _timesheet_create_task_prepare_values(self, project):
        task_vals = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        task_vals.update(completion_elligible=self.product_id.completion_elligible)
        return task_vals
    
    @api.multi
    def _compute_forecasted_amount(self):
        """
        This methods sums the total of forecast potential revenues.
        Triggered by the forecast write/create methods
        """
        forecasts = self.env['project.forecast'].search('order_line_id','=',id)
        _logger.info("Hours {} Rates {} TOTAL {}".format(forecasts.mapped('resource_hours'),forecasts.mapped('hourly_rate'),forecasts.mapped('resource_hours')*forecasts.mapped('hourly_rate')))
        return 0.0
