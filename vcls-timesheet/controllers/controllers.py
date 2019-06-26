import babel
from dateutil.relativedelta import relativedelta
import itertools
import json
from odoo import http, fields, _
from odoo.http import request
from odoo.tools import float_round

from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController

class TimesheetController(SaleTimesheetController):

    def _plan_get_stat_button(self, projects):
        stat_buttons = super(TimesheetController,self)._plan_get_stat_button(projects)

        stat_buttons.append({
            'name': _('Report Analysis'),
            'res_model': 'project.timesheet.forecast.report.analysis',
            'domain': [('project_id', 'in', projects.ids)],
            'icon': 'fa fa-calendar',
        })
        return stat_buttons

    @http.route('/timesheet/plan/action', type='json', auth="user")
    def plan_stat_button(self, domain=[], res_model='account.analytic.line', res_id=False):
        if res_model == 'project.timesheet.forecast.report.analysis':
            ts_view_graph_id = request.env.ref('project_timesheet_forecast.project_timesheet_forecast_report_view_graph').id
            ts_view_pivot_id = request.env.ref('project_timesheet_forecast.project_timesheet_forecast_report_view_pivot').id
            ts_search_view_id = request.env.ref('project_timesheet_forecast.project_timesheet_forecast_report_view_search').id
            action = {
                'name': _('Report Analysis'),
                'type': 'ir.actions.act_window',
                'res_model': res_model,
                'view_mode': 'graph,pivot',
                'views': [[ts_view_graph_id, 'graph'], [ts_view_pivot_id, 'pivot']],
                'domain': domain,
                'context' : {
                    'pivot_row_groupby': ['employee_id'],
                    'pivot_col_groupby': ['date', 'type'],
                    'pivot_measures': ['number_hours'],
                    'group_by': ['date:month', 'type'],
                    'search_default_year': True,},
                'search_view_id': ts_search_view_id,
            }
        else:
            action = super(TimesheetController,self).plan_stat_button(domain,res_model,res_id)
        return action 