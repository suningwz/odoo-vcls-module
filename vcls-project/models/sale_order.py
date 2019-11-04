# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'
    parent_project_id = fields.Many2one(
        'project.project', compute='_get_parent_project_id'
    )
    family_task_count = fields.Integer(
        'Family Task Count', compute='_get_family_task_count'
    )

    forecasted_amount = fields.Monetary(
        compute = "_compute_forecasted_amount",
        store = True,
        default = 0.0,
    )

    @api.multi
    def _get_parent_project_id(self):
        for project in self:
            project.parent_project_id = project.parent_id.project_id if self.parent_id else self.project_id

    @api.multi
    def _get_family_task_count(self):
        for project in self:
            parent_project, child_projects = self._get_family_projects()
            family_projects = (parent_project | child_projects)
            project.family_task_count = len(family_projects.mapped('tasks'))


    @api.multi
    def quotation_program_print(self):
        """ Print all quotation related to the program
        """
        programs = self.mapped('program_id')
        quot = self.search([('program_id', 'in', programs.ids), ('state', '=', 'draft')])
        return self.env.ref('sale.action_report_saleorder').report_action(quot)

    @api.multi
    def action_view_project_ids(self):
        self.ensure_one()
        parent_project = self.parent_id.project_id
        if parent_project and self.env.user.has_group('project.group_project_manager'):
            action = parent_project.action_view_timesheet_plan()
            return action
        return super(SaleOrder, self).action_view_project_ids()

    @api.multi
    def action_view_family_parent_project(self):
        self.ensure_one()
        parent_project_id = self.parent_id.project_id if self.parent_id else self.project_id
        if not parent_project_id:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'name': _('Project'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.project',
            'res_id': parent_project_id.id,
            'view_id': False,
            'context': self.env.context,
        }

    @api.multi
    def action_view_family_parent_tasks(self):
        self.ensure_one()
        parent_project, child_projects = self._get_family_projects()
        return {
            'name': _('Tasks'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,calendar,pivot,graph,activity',
            'res_model': 'project.task',
            'domain': [('project_id', 'in', (parent_project | child_projects).ids)],
            'context': {
                'search_default_project_id': self.project_id.id,
            },
        }
    
    def _compute_forecasted_amount(self):
        """
        This methods sums the total of forecast potential revenues.
        Triggered by the forecast write/create methods
        """
        #forecasts = self.env['project.forecast'].search('order_line_id')
        return 0.0

