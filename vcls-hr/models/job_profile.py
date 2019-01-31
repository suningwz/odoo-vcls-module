# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class job_profile(models.Model):
    
    _name = 'hr.job_profile'
    _description = 'Job Profile'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char(
        required=True,
        compute='_compute_name',)
    
    info_string = fields.Char()
    
    description = fields.Text()
    
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required="True",)
    
    employee_company_id = fields.Many2one(
        'res.company',
        related='employee_id.company_id',)
    
    job1_id = fields.Many2one(
        'hr.job',
        string="Primary Position",
        required = True,)
    
    job1_percentage = fields.Float(
        string="Primary Working %",
        required=True,
        default=1.0,)
    
    job1_target = fields.Float(
        related="job1_id.billable_target_percentage",
        string="Primary Target %",
        readonly="1",)
    
    job1_head = fields.Many2one(
        'hr.employee',
        related='job1_id.vcls_activity_id.head_id',
        readonly='1',
        string='Primary Head of Activity')
    
    job1_dir = fields.Many2one(
        'hr.employee',
        related='job1_id.department_id.manager_id',
        string='Primary Head of Department')
    
    job2_id = fields.Many2one(
        'hr.job',
        string="Secondary Position",)
    
    job2_percentage = fields.Float(
        string="Secondary Working %",)
    
    job2_target = fields.Float(
        related="job2_id.billable_target_percentage",
        string="Secondary Target %",)
    
    job2_head = fields.Many2one(
        'hr.employee',
        related='job2_id.vcls_activity_id.head_id',
        readonly='1',
        string='Secondary Head',)
    
    job2_dir = fields.Many2one(
        'hr.employee',
        related='job2_id.department_id.manager_id',
        string='Secondary Head of Department')
    
    manager_ids = fields.Many2many(
        'res.users',
        compute = '_get_managers')
    
    '''
    total_working_percentage = fields.Float(
        string="Total Working %",
        compute='_compute_aggregations',)
    
    total_working_hours = fields.Float(
        string="Total Working Hours",
        compute='_compute_aggregations',)
    
    total_billable_target = fields.Float(
        string="Total Billable Target",
        compute='_compute_aggregations',)
    '''
    
    resource_calendar_id = fields.Many2one(
        'resource.calendar',
        string='Working Time',
        required=True,
        )
  
    ###################
    # Compute Methods #
    ###################
    
    @api.depends('job1_head','job2_head','job1_dir','job2_dir')
    def _get_managers(self):
        for rec in self:
            rec.manager_ids = False
            rec.manager_ids |= rec.job1_head.user_id
            rec.manager_ids |= rec.job2_head.user_id
            rec.manager_ids |= rec.job1_dir.user_id
            rec.manager_ids |= rec.job2_dir.user_id
    
    @api.depends('job1_id','job1_percentage','job2_id','job2_percentage')
    def _compute_name(self):
        for rec in self:
            #build the name for easier search and info
            if rec.job1_id: 
                rec.name = '{} at {:.0f}%'.format(rec.job1_id.name, 100*rec.job1_percentage)
            if rec.job2_id:
                rec.name += ' | {} at {:.0f}%'.format(rec.job2_id.name, 100*rec.job2_percentage)
    '''         
    @api.depends('job1_id','job1_percentage','job1_target','job2_id','job2_percentage','job2_target','employee_id.resource_calendar_id')
    def _compute_aggregations(self):
        for rec in self:
            rec.total_working_percentage = rec.job1_percentage + rec.job2_percentage
            rec.total_working_hours = rec.total_working_percentage*rec.employee_id.resource_calendar_id.hours_per_day*5 #averaged over 5 days a week
            rec.total_billable_target = (rec.job1_percentage*rec.job1_target+rec.job2_percentage*rec.job2_target)*rec.employee_id.resource_calendar_id.hours_per_day*5
            
            #build the name for easier search and info
            rec._compute_name()
    ''' 
    
    @api.constrains('job1_percentage','job2_percentage')
    def check_working_percentage(self):
        for jp in self:
            if (jp.job1_percentage + jp.job2_percentage)>1.0:
                raise ValidationError("Impossible to configure more than 100% working time.")
    
    