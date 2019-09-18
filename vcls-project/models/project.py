# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

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
    
    parent_id = fields.Many2one('project.project', 'Parent project', index=True, ondelete='cascade')
    child_id = fields.One2many('project.project', 'parent_id', 'Child projects')

    parent_task_count = fields.Integer(
        compute = '_compute_parent_task_count'
    )

    child_task_count = fields.Integer(
        compute = '_compute_child_task_count'
    )

    #consultant_ids = fields.Many2many('hr.employee', string='Consultants')
    #ta_ids = fields.Many2many('hr.employee', string='Ta')
    completion_ratio = fields.Float('Project completion', compute='compute_project_completion_ratio', store=True)
    consumed_value = fields.Float('Consumed value', compute='compute_project_consumed_value', store=True)
    consummed_completed_ratio = fields.Float('Consumed / Completion',
                                             compute='compute_project_consummed_completed_ratio', store=True)

    ##################
    # CUSTOM METHODS #
    ##################
    @api.multi
    def get_tasks_for_project_sub_project(self):
        """This function will return all the tasks and subtasks found in the main and Child
        Projects which participates in KPI's"""
        self.ensure_one()
        tasks = self.task_ids + self.child_id.task_ids
        all_tasks = tasks + tasks.mapped('child_ids')
        return all_tasks.filtered(lambda task: task.sale_line_id.product_id.completion_elligible and
                                  task.stage_id.status not in  ['not_started','cancelled'])

    ###############
    # ORM METHODS #
    ###############
    @api.model
    def create(self, vals):
        if 'project_type' in vals: 
            if vals['project_type'] == 'client':
                vals['privacy_visibility'] = 'employees'
            else:
                vals['privacy_visibility'] = 'followers'
        
        #we automatically assign the project manager to be the one defined in the core team
        if vals.get('sale_order_id',False):
            so = self.env['sale.order'].browse(vals.get('sale_order_id'))
            lc = so.core_team_id.lead_consultant
            _logger.info("SO info {}".format(lc.name))
            if lc:
                vals['user_id']=lc.user_id.id


        project = super(Project, self).create(vals)
        ids = project._get_default_type_common()
        project.type_ids = ids if ids else project.type_ids
        
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
