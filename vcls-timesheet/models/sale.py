from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError
import datetime

class SaleOrder(models.Model):
    _inherit='sale.order'
    @api.multi
    def action_view_forecast(self):
        self.ensure_one()
        project_ids = self.project_ids
        return {
            'type': 'ir.actions.act_window',
            'name': "Forecast",
            'res_model': 'project.forecast',
            'search_view_id': self.env.ref('project_timesheet_forecast.project_timesheet_forecast_report_view_search').id,
            'view_mode': 'graph,pivot',
            'context': {
                'project_id': project_ids.id,
                'default_project_id': project_ids.id, 
                'search_default_project_id': [project_ids.id],
                'grid_anchor': (datetime.date.today()).strftime('%Y-%m-%d'),
            }
        }