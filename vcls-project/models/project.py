# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError

import logging

_logger = logging.getLogger(__name__)


class Project(models.Model):

    _name = 'project.project'
    _inherit = ['project.project', 'mail.thread', 'mail.activity.mixin']

    # We Override this method from 'project_task_default_stage
    def _get_default_type_common(self):
        ids = self.env['project.task.type'].search([
            ('case_default', '=', True),
            ('project_type_default', '=', self.project_type)])
        _logger.info("Default Stages: {} for project type {}".format(ids.mapped('name'),self.project_type))
        return ids

    type_ids = fields.Many2many(
        default=lambda self: self._get_default_type_common())

    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self._default_user_id() , track_visibility="onchange")

    project_type = fields.Selection([
        ('dev', 'Developement'),
        ('client', 'Client'),
        ('internal','Internal')],
        string = 'Project Type',
        default = 'client',
    )

    # Maximum parent level here is meant to be 1 at max for now
    parent_id = fields.Many2one(
        'project.project', 'Parent project',
        index=True, ondelete='cascade',
        compute='_get_parent_id',
        store=True
    )
    child_id = fields.One2many('project.project', 'parent_id', 'Child projects')

    parent_task_count = fields.Integer(
        compute='_compute_parent_task_count'
    )

    child_task_count = fields.Integer(
        compute='_compute_child_task_count'
    )

    #consultant_ids = fields.Many2many('hr.employee', string='Consultants')
    #ta_ids = fields.Many2many('hr.employee', string='Ta')
    completion_ratio = fields.Float('Task Complete', compute='compute_project_completion_ratio', store=True)
    consumed_value = fields.Float('Budget Consumed', compute='compute_project_consumed_value', store=True)
    consummed_completed_ratio = fields.Float('Budget Consumed/Task Complete',
                                             compute='compute_project_consummed_completed_ratio', store=True)
    summary_ids = fields.One2many(
        'project.summary', 'project_id',
        'Project summaries'
    )
    is_project_manager = fields.Boolean(compute="_get_is_project_manager")
    scope_of_work = fields.Html(string='Scope of work')
    orders_count = fields.Integer(compute='compute_orders_count')
    tasks_count = fields.Integer()
    timesheets_count = fields.Integer()
    lead_consultant = fields.Many2one('hr.employee', related='core_team_id.lead_consultant', string='Lead Consultant')
    lead_backup = fields.Many2one('hr.employee', related='core_team_id.lead_backup',
                                  string='Lead Consultant Backup')
    consultant_ids = fields.Many2many('hr.employee', 'rel_project_consultants', related='core_team_id.consultant_ids',
                                      string='Consultants')
    ta_ids = fields.Many2many('hr.employee', relation='rel_project_tas', related='core_team_id.ta_ids',
                              string='Ta')

    invoices_count = fields.Integer(
        compute='_get_out_invoice_ids',
        compute_sudo = True
    )
    out_invoice_ids = fields.Many2many(
        string='Out invoices',
        compute='_get_out_invoice_ids',
        comodel_name="account.invoice",
        relation="project_out_invoice_rel",
        column1="project_id",
        column2="invoice_id",
        store=True,
        copy=False, readonly=True,
        compute_sudo=True
    )

    risk_ids = fields.Many2many(
        'risk', string='Risk',
        compute='_get_risks',
    )

    risk_score = fields.Integer(
        string='Risk Score',
        compute='_compute_risk_score',
        store=True,
    )

    def _get_risks(self):
        for project in self:
            project.risk_ids = self.env['risk'].search([
                ('resource', '=', 'project.project,{}'.format(project.id)),
            ])

    @api.depends('risk_ids', 'risk_ids.score')
    def _compute_risk_score(self):
        for project in self:
            project.risk_score = sum(project.risk_ids.mapped('score'))

    @api.one
    @api.depends(
        'sale_line_id.order_id.order_line.invoice_lines',
        'tasks.sale_order_id',
    )
    def _get_out_invoice_ids(self):
        # use of sudo here because of the non possibility of lc to read some invoices
        project_sudo = self.sudo()
        out_invoice_ids = project_sudo.mapped('sale_line_id.order_id.invoice_ids') \
            | project_sudo.mapped('tasks.sale_order_id.invoice_ids')
        self.out_invoice_ids = out_invoice_ids
        self.invoices_count = len(out_invoice_ids)

    @api.multi
    @api.depends(
        'sale_order_id', 'sale_order_id.parent_id',
        'sale_order_id.parent_id.project_id'
    )
    def _get_parent_id(self):
        for project in self:
            if project.sale_order_id:
                project.parent_id = project.sale_order_id.parent_id.project_id

    ##################
    # CUSTOM METHODS #
    ##################
    @api.multi
    def get_tasks_for_project_sub_project(self):
        """This function will return all the tasks and subtasks found in the main and Child
        Projects which participates in KPI's"""
        self.ensure_one()
        tasks = self.task_ids + self.child_id.mapped('task_ids')
        all_tasks = tasks + tasks.mapped('child_ids')
        return all_tasks.filtered(lambda task: task.sale_line_id.product_id.completion_elligible and
                                  task.stage_id.status not in  ['not_started','cancelled'])

    @api.multi
    def action_raise_new_invoice(self):
        """This function will trigger the Creation of invoice regrouping all the sale orders."""
        orders = self.env['sale.order']
        for project in self:
            if not project.sale_order_id and project.sale_order_id.invoice_status != 'to invoice':
                raise UserError(_("The selected Sales Order should contain something to invoice."))
            else:
                orders |= project.sale_order_id

        action = self.env.ref('sale.action_view_sale_advance_payment_inv').read()[0]
        action['context'] = {
            'active_ids': orders.ids
        }
        return action

    @api.multi
    def action_raise_new_risk(self):
        self.ensure_one()
        action = self.env.ref('vcls-risk.action_view_risk_wizard').read()[0]
        action['context'] = {
            'default_resource': 'project.project,{}'.format(self.id),
            'new_risk':True,
        }
        return action

    @api.multi
    def show_risks(self):
        self.ensure_one()
        action = self.env.ref('vcls-risk.action_view_risk').read()[0]
        action['domain'] = [('resource', '=', 'project.project,{}'.format(self.id))]
        action['target'] = 'current'
        return action

    @api.multi
    def sale_orders_tree_view(self):
        action = self.env.ref('sale.action_quotations').read()[0]
        action['domain'] = [('project_id', 'child_of', self.id)]
        action['context'] = {}
        return action

    @api.multi
    def invoices_tree_view(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['domain'] = [('id', 'in', self.out_invoice_ids.ids)]
        return action

    @api.multi
    def tasks_tree_view(self):
        action = self.env.ref('project.act_project_project_2_project_task_all').read()[0]
        return action

    @api.multi
    def forecasts_tree_view(self):
        action = self.env.ref('project_forecast.project_forecast_action_from_project').read()[0]
        action['domain'] = [('project_id', 'child_of', self.id)]
        return action

    @api.multi
    def timesheets_tree_view(self):
        action = self.env.ref('hr_timesheet.act_hr_timesheet_line_by_project').read()[0]
        action['domain'] = [('project_id', 'child_of', self.id)]
        return action

    @api.multi
    def report_analysis_tree_view(self):
        action = self.env.ref('vcls-timesheet.project_timesheet_forecast_report_action').read()[0]
        action['domain'] = [('project_id', 'child_of', self.id)]
        action['context'] = {'active_id': self.id, 'active_model': 'project.project'}
        return action

    ###############
    # ORM METHODS #
    ###############
    @api.model
    def create(self, vals):

        #default visibility
        vals['privacy_visibility'] = 'portal'
        
        #we automatically assign the project manager to be the one defined in the core team
        if vals.get('sale_order_id',False):
            so = self.env['sale.order'].browse(vals.get('sale_order_id'))
            vals['scope_of_work'] = so.scope_of_work
            lc = so.core_team_id.lead_consultant
            _logger.info("SO info {}".format(lc.name))
            if lc:
                vals['user_id']=lc.user_id.id


        project = super(Project, self).create(vals)
        ids = project._get_default_type_common()
        project.type_ids = ids if ids else project.type_ids

        if project.project_type != 'client':
            project.privacy_visibility = 'employees'
        
        return project
    

    ###################
    # COMPUTE METHODS #
    ###################

    @api.model
    def _default_user_id(self):
        if self.project_type == 'client': 
            if self.sale_order_id:
                return self.sale_order_id.opportunity_id.user_id  
        return self.env.user

    def _compute_parent_task_count(self):
        task_data = self.env['project.task'].read_group([('parent_id','=',False),('project_id', 'in', self.ids), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.parent_task_count = result.get(project.id, 0)
    
    def _compute_child_task_count(self):
        task_data = self.env['project.task'].read_group([('parent_id','!=',False),('project_id', 'in', self.ids), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.child_task_count = result.get(project.id, 0)
    
    def _compute_task_count(self):
        read_group_res = self.env['project.task'].read_group([('project_id', 'child_of', self.ids), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])
        group_data = dict((data['project_id'][0], data['project_id_count']) for data in read_group_res)
        for project in self:
            task_count = 0
            for sub_project_id in project.search([('id', 'child_of', project.id)]).ids:
                task_count += group_data.get(sub_project_id, 0)
            project.task_count = task_count

    @api.multi
    @api.depends('task_ids.completion_ratio')
    def compute_project_completion_ratio(self):
        for project in self:
            tasks = project.get_tasks_for_project_sub_project()
            project.completion_ratio = sum(tasks.mapped('completion_ratio')) / len(tasks) if tasks else sum(tasks.mapped('completion_ratio'))

    @api.multi
    @api.depends('task_ids.progress')
    def compute_project_consumed_value(self):
        for project in self:
            tasks = project.get_tasks_for_project_sub_project()
            #_logger.info("TASK FOUND {} with {}".format(tasks.mapped('name'),tasks.mapped('progress')))
            project.consumed_value = sum(tasks.mapped('progress')) / len(tasks) if tasks \
                else sum(tasks.mapped('progress'))

    @api.multi
    @api.depends('task_ids.consummed_completed_ratio')
    def compute_project_consummed_completed_ratio(self):
        for project in self:
            tasks = project.get_tasks_for_project_sub_project()
            project.consummed_completed_ratio = sum(tasks.mapped('consummed_completed_ratio')) / len(tasks) if tasks else sum(tasks.mapped('consummed_completed_ratio'))

    @api.multi
    def _get_is_project_manager(self):
        for p in self:
            p.is_project_manager = p.user_id == self.env.user

    @api.multi
    def compute_orders_count(self):
        for project in self:
            project.orders_count = self.env['sale.order'].search_count([('project_id', 'child_of', project.id)])

    @api.multi
    def compute_invoices_count(self):
        self.ensure_one()
        projects = self.env['project.project'].search([('id', 'child_of', self.id)])
        sale_orders = projects.mapped('sale_line_id.order_id') | projects.mapped('tasks.sale_order_id')
        invoices = sale_orders.mapped('invoice_ids').filtered(lambda inv: inv.type == 'out_invoice')
        self.invoices_count = len(invoices)

    @api.multi
    def toggle_active(self):
        if any(project.activity_ids for project in self):
            raise ValidationError(_("Its not possible to archive a project while there is still undone activities "))
        super(Project, self).toggle_active()

    @api.model
    def end_project_activities_scheduling(self):
        for project_id in self.search([('active', '=', True), ('parent_id', '=', False)]):
            task_ids = [task for child_id in project_id.child_id for task in child_id.task_ids]
            if task_ids and all(task.stage_id.status in ("completed", "cancelled") for task in task_ids):
                users_summary = {
                    project_id.partner_id.user_id.id: _('Client Feedback'),
                    project_id.user_id.id: _('End of project form filling'),
                    project_id.partner_id.invoice_admin_id.id: _('Invoicing Closing')
                }
                for user_id, summary in users_summary.items():
                    if user_id:
                        activity_vals = {
                            'user_id': user_id,
                            'summary': summary,
                            'act_type_xmlid': 'mail.mail_activity_data_todo',
                            'automated': True,
                        }
                        project_id.sudo().activity_schedule(**activity_vals)
        return True
