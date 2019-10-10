# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'
    
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

