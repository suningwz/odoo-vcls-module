from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit='sale.order'
    @api.multi
    def action_view_forecast(self):
        self.ensure_one()
        project_ids = self.project_ids
        return {
            'type': 'ir.actions.act_window',
            'name': "Forecast",
            'domain': [('project_id', '!=', False)],
            'res_model': 'project.timesheet.forecast.report.analysis',
            'search_view_id': self.env.ref('project_timesheet_forecast.project_timesheet_forecast_report_view_search').id,
            'view_mode': 'graph,pivot',
            'context': {
                'pivot_row_groupby': ['employee_id'],
                'pivot_col_groupby': ['date', 'type'],
                'pivot_measures': ['number_hours'],
                'group_by': ['date:month', 'type'],
                'search_default_year': True,
                'default_project_id': project_ids.id, 
                'search_default_project_id': [project_ids.id], 
            }
        }