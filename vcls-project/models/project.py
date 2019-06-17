# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self._default_user_id() , track_visibility="onchange")

    project_type = fields.Selection([
        ('dev', 'Developement'),
        ('client', 'Client'),
        ('internal','Internal')],
        string = 'Project Type',
        default = 'internal',
    )

    parent_task_count = fields.Integer(
        compute = '_compute_parent_task_count'
    )

    child_task_count = fields.Integer(
        compute = '_compute_child_task_count'
    )

    

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
