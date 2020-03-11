# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'

    time_category_ids = fields.Many2many(
        'project.time_category',
        string='Time Categories',
        )
    connected_employee_seniority_level_id = fields.Many2one(
        comodel_name='hr.employee.seniority.level',
        compute='_get_connected_employee_seniority_level_id',
        string='Default Seniority'
    )
    date_start = fields.Datetime(default=False)
    date_deadline = fields.Date(
        store=True,
        compute = '_compute_deadline',
    )

    last_updated_timesheet_date = fields.Datetime(
        compute='get_last_updated_timesheet_date',
        compute_sudo=True,
        store=True
    )
    forecast_ids = fields.One2many(
        'project.forecast',
        'task_id'
    )

    contractual_budget = fields.Float(string="Contractual Budget",readonly=True)
    forecasted_budget = fields.Float(string="Forecasted Budget",readonly=True)
    realized_budget = fields.Float(string="Realized Budget",readonly=True)
    valued_budget = fields.Float(string="Valued Budget",readonly=True)
    invoiced_budget = fields.Float(string="Invoiced Budget",readonly=True)

    forecasted_hours = fields.Float(string="Forecasted Hours",readonly=True)
    realized_hours = fields.Float(string="Realized Hours",readonly=True)
    valued_hours = fields.Float(string="Valued Hours",readonly=True)
    invoiced_hours = fields.Float(string="Invoiced Hours",readonly=True)
    valuation_ratio = fields.Float(string="Valuation Ratio",readonly=True)
    recompute_kpi = fields.Boolean(compute='_get_to_recompute', store=True)

    pc_budget = fields.Float(string="PC Review Budget",readonly=True)
    cf_budget = fields.Float(string="Carry Forward Budget",readonly=True)
    pc_hours = fields.Float(string="PC Review Hours",readonly=True)
    cf_hours = fields.Float(string="Carry Forward Hours",readonly=True)

    @api.depends('date_end')
    def _compute_deadline(self):
        for task in self:
            if task.date_end:
                task.date_deadline = task.date_end.date()

    @api.depends(
        'sale_line_id.price_unit',
        'sale_line_id.product_uom_qty',
        'forecast_ids.hourly_rate',
        'forecast_ids.resource_hours',
        'timesheet_ids.stage_id',
        'timesheet_ids.unit_amount',
        'timesheet_ids.unit_amount_rounded',
    )
    def _get_to_recompute(self):
        for task in self:
            task.recompute_kpi = True

    @api.model
    def _cron_compute_kpi(self,force=False):
        if force:
            tasks = self.search([])
        else:
            tasks = self.search([('recompute_kpi', '=', True)])
            
        projects = self.env['project.project']
        tasks._get_kpi()
        for task in tasks:
            task.recompute_kpi = False
            projects |= task.project_id
        projects._get_kpi()
        # self._cr.execute('update project_task set ')

    @api.multi
    def _get_kpi(self):
        for task in self:
            task.contractual_budget = task.sale_line_id.price_unit * task.sale_line_id.product_uom_qty
            task.forecasted_budget = sum([
                hourly_rate * resource_hours for hourly_rate, resource_hours in
                zip(task.forecast_ids.mapped('hourly_rate'), task.forecast_ids.mapped('resource_hours'))
            ])
            task.realized_budget = sum(
                task.timesheet_ids.filtered(lambda t: t.stage_id not in ('draft', 'outofscope'))
                    .mapped(lambda t:t.unit_amount * t.so_line_unit_price)
            )
            task.valued_budget = sum(
                task.timesheet_ids.filtered(lambda t: t.stage_id not in ('draft', 'outofscope'))
                    .mapped(lambda t:t.unit_amount_rounded * t.so_line_unit_price)
            )
            task.pc_budget = sum(
                task.timesheet_ids.filtered(lambda t: t.stage_id in ('pc_review'))
                    .mapped(lambda t:t.unit_amount_rounded * t.so_line_unit_price)
            )
            task.cf_budget = sum(
                task.timesheet_ids.filtered(lambda t: t.stage_id in ('carry_forward'))
                    .mapped(lambda t:t.unit_amount_rounded * t.so_line_unit_price)
            )
            task.invoiced_budget = sum(
                task.timesheet_ids.filtered(lambda t: t.stage_id == 'invoiced')
                    .mapped(lambda t:t.unit_amount_rounded * t.so_line_unit_price)
            )
            task.forecasted_hours = sum(task.forecast_ids.mapped('resource_hours'))
            task.realized_hours = sum(task.timesheet_ids.filtered(
                lambda t: t.stage_id not in ('draft', 'outofscope')
            ).mapped('unit_amount'))
            task.valued_hours = sum(task.timesheet_ids.filtered(
                lambda t: t.stage_id not in ('draft', 'outofscope')
            ).mapped('unit_amount_rounded'))
            task.pc_hours = sum(task.timesheet_ids.filtered(
                lambda t: t.stage_id in ('pc_review')
            ).mapped('unit_amount_rounded'))
            task.cf_hours = sum(task.timesheet_ids.filtered(
                lambda t: t.stage_id in ('carry_forward')
            ).mapped('unit_amount_rounded'))
            task.invoiced_hours = sum(task.timesheet_ids.filtered(
                lambda t: t.stage_id == 'invoiced'
            ).mapped('unit_amount_rounded'))

            task.valuation_ratio = 100.0*(task.valued_hours / task.realized_hours) if task.realized_hours else False

            #task.sale_line_id._compute_untaxed_amount_to_invoice()

    @api.onchange('sale_line_id')
    def _onchange_lead_id(self):
        if not self.date_start:
            date_start = self.sale_line_id.order_id.expected_start_date
            if date_start:
                self.date_start = datetime.fromordinal(date_start.toordinal())
        if not self.date_end:
            date_end = self.sale_line_id.order_id.expected_end_date or fields.Datetime.now()
            if date_end:
                self.date_end = datetime.fromordinal(date_end.toordinal())
    
    @api.onchange('parent_id')
    def get_parent_categories(self):
        if self.parent_id:
            self.time_category_ids = self.parent_id.time_category_ids
        else:
            self.time_category_ids = False

    @api.multi
    def _get_connected_employee_seniority_level_id(self):
        user_id = self.env.user.id
        connected_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
        seniority_level_id = connected_employee_id.seniority_level_id
        for line in self:
            line.connected_employee_seniority_level_id = seniority_level_id

    @api.model
    def create(self, vals):
        #we catch the parent time categories if this is a subtask
        if vals.get('parent_id',False):
            parent_task = self.browse(vals['parent_id'])
            if parent_task.time_category_ids:
                vals.update({
                    'time_category_ids': [(6, 0, parent_task.time_category_ids.ids)]
                })
        else:
            travel_category_id = self.env.ref('vcls-timesheet.travel_time_category')
            
            if vals.get('time_category_ids', False):
                time_cat = vals['time_category_ids']
            else:
                time_cat = []
            
            if travel_category_id:
                time_cat = list(set(time_cat.append(travel_category_id.id)))
            
            vals.update({'time_category_ids': [(6,0,time_cat)]})

            """if travel_category_id:
                if time_categories:
                    if travel_category_id not in vals['time_category_ids'][0][2]:
                        vals['time_category_ids'][0][2].append(travel_category_id.id)
                else:
                    vals.update({'time_category_ids': [[6, False, [travel_category_id.id]]]})"""

        task = super(ProjectTask, self).create(vals)

        # Update end and start date according to related sale_order estimated dates
        if not task.date_start:
            date_start = task.sale_line_id.order_id.expected_start_date
            if date_start:
                task.date_start = datetime.fromordinal(date_start.toordinal())
        if not task.date_end:
            date_end = task.sale_line_id.order_id.expected_end_date
            if date_end:
                task.date_end = datetime.fromordinal(date_end.toordinal())
        return task

    @api.one
    @api.depends('timesheet_ids', 'timesheet_ids.write_date', 'child_ids', 'child_ids.timesheet_ids',
                 'child_ids.timesheet_ids.write_date')
    def get_last_updated_timesheet_date(self):
        timesheets = self.timesheet_ids | self.child_ids.mapped('timesheet_ids')
        if timesheets:
            self.last_updated_timesheet_date = timesheets.sorted(key=lambda wd: wd.write_date, reverse=True)[0]\
                .write_date

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('desc_order_display'):
            domain = list(args)
            domain.append(('last_updated_timesheet_date', '!=', False))
            new_order = 'last_updated_timesheet_date desc'
            las_res = super(ProjectTask, self)._search(domain, offset=offset, limit=limit, order=new_order,
                                                       count=count, access_rights_uid=access_rights_uid)
            domain = list(args)
            domain.append(('last_updated_timesheet_date', '=', False))
            res = super(ProjectTask, self)._search(domain, offset=offset, limit=limit, order=order,
                                                   count=count, access_rights_uid=access_rights_uid)
            return las_res + res
        return super(ProjectTask, self)._search(args, offset=offset, limit=limit, order=order,
                                                count=count, access_rights_uid=access_rights_uid)

    @api.multi
    def action_view_forecast(self):
        self.ensure_one()
        action = self.env.ref('vcls-project.project_forecast_action').read()[0]
        action['domain'] = [('task_id', '=', self.id)]
        action['context'] = {
            'default_task_id': self.id,
            'default_project_id': self.project_id.id,
            'default_search_task_id': self.id,
            'search_default_group_by_project_id': 1,
            'search_default_group_by_task_id': 1,
        }
        return action


class Project(models.Model):
    _inherit = 'project.project'

    # to be used to order projects according to time coding
    last_updated_timesheet_date = fields.Datetime(compute='get_last_updated_timesheet_date', compute_sudo=True,
                                                  store=True)
    timesheet_ids = fields.One2many('account.analytic.line', 'project_id')

    @api.one
    @api.depends('timesheet_ids', 'timesheet_ids.write_date', 'child_id', 'child_id.timesheet_ids',
                 'child_id.timesheet_ids.write_date')
    def get_last_updated_timesheet_date(self):
        timesheets = self.timesheet_ids | self.child_id.mapped('timesheet_ids')
        if timesheets:
            self.last_updated_timesheet_date = timesheets.sorted(key=lambda wd: wd.write_date, reverse=True)[
                0].write_date

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('related_core_team_projects'):
            user_related_core_teams = self.env['core.team'].search([('user_ids', '=', self.env.uid)])
            last_user_updated_timesheets = self.env['account.analytic.line'].search([('user_id', '=', self.env.uid)])
            if user_related_core_teams:
                args += [('core_team_id', 'in', user_related_core_teams.ids),
                         ('timesheet_ids', 'in', last_user_updated_timesheets.ids)]
            domain = list(args)
            domain.append(('last_updated_timesheet_date', '!=', False))
            new_order = 'last_updated_timesheet_date desc'
            las_res = super(Project, self)._search(domain, offset=offset, limit=limit, order=new_order,
                                                   count=count, access_rights_uid=access_rights_uid)
            domain = list(args)
            domain.append(('last_updated_timesheet_date', '=', False))
            res = super(Project, self)._search(domain, offset=offset, limit=limit, order=order,
                                               count=count, access_rights_uid=access_rights_uid)
            return las_res + res
        return super(Project, self)._search(args, offset=offset, limit=limit, order=order,
                                            count=count, access_rights_uid=access_rights_uid)

    @api.multi
    def _action_view_project_forecast(self):
        self.ensure_one()
        action = self.env.ref('vcls-project.project_forecast_action').read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'group_by': ['project_id', 'deliverable_id', 'task_id'],
            'default_project_id': self.id,
            'active_id': self.id,
        }
        return action
