# -*- coding: utf-8 -*-
from ast import literal_eval
import babel
from dateutil.relativedelta import relativedelta
import itertools
import json

from odoo import http, fields, _
from odoo.http import request
from odoo.tools import float_round

from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController


class TimesheetController(SaleTimesheetController):

    @http.route('/timesheet/plan/action', type='json', auth="user")
    def plan_stat_button(self, domain=[], res_model='account.analytic.line', res_id=False):
        if res_model == 'account.analytic.line':
            ts_view_tree_id = request.env.ref('hr_timesheet.timesheet_view_tree_user').id
            ts_view_form_id = request.env.ref('hr_timesheet.hr_timesheet_line_form').id
            action = {
                'name': _('Timesheets'),
                'type': 'ir.actions.act_window',
                'res_model': res_model,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'views': [[ts_view_tree_id, 'list'], [ts_view_form_id, 'form']],
                'domain': domain,
                'context': {"search_default_groupby_deliverable":1, 
                "search_default_groupby_task":1}, 
            }
        else:
            action = super(TimesheetController,self).plan_stat_button(domain,res_model,res_id)
        return action