# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class ProjectProgram(models.Model):

    _name = 'project.program'
    _description = 'Client Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        required = True,
    )

    active = fields.Boolean(
        default = True,
    )

    client_id = fields.Many2one(
        comodel_name = 'res.partner',
        domain = "[('customer','=',True)]",
        string = 'Related Client',
        required = True,
    )

    leader_id = fields.Many2one(
        comodel_name = 'res.users',
        string = 'Program Leader',
    )

    product_name = fields.Char(
        string = "Product Name",
        help = 'The client product name',
    )

    client_product_ids = fields.Many2many(
        comodel_name = 'client.product',
        string = 'Client Product',
    )

   
    app_country_group_id = fields.Many2one(
        'res.country.group',
        string = "Application Geographic Area",
    )

    prim_therapeutic_area_id = fields.Many2one(
        'therapeutic.area',
    )

    prim_indication_id = fields.Many2one(
       'targeted.indication', 
    )

    prim_detailed_indication = fields.Text()

    sec_therapeutic_area_id = fields.Many2one(
        'therapeutic.area',
    )

    sec_indication_id = fields.Many2one(
       'targeted.indication', 
    )

    sec_detailed_indication = fields.Text()

    """therapeutic_area_ids = fields.Many2many(
        'therapeutic.area',
        string ='Therapeutic Area',
    )
    
    targeted_indication_ids = fields.Many2many(
        'targeted.indication',
        string ='Targeted Indication',
    )"""

     # Only 4 input so no need to create new object
    stage_id =  fields.Selection([('pre', 'Preclinical'),('exploratory', 'Exploratory Clinical'),
    ('confirmatory', 'Confirmatory Clinical'), ('post', 'Post Marketing')], 'Stage', default='pre')
    
    product_description = fields.Char()
    
    sale_order_count = fields.Integer(compute='_compute_sale_order_count', string='Sale Order Count')
    opportunity_count = fields.Integer(compute='_compute_opportunity_count', string='Opportunity Count')
    project_count = fields.Integer(compute='_compute_project_count', string='Main Project Count')

   
    
    def _compute_sale_order_count(self):
        order_data = self.env['sale.order'].read_group([('program_id', 'in', self.ids)], ['program_id'], ['program_id'])
        result = dict((data['program_id'][0], data['program_id_count']) for data in order_data)
        for program in self:
            program.sale_order_count = result.get(program.id, 0)
    
    def _compute_opportunity_count(self):
        lead_data = self.env['crm.lead'].read_group([('program_id', 'in', self.ids)], ['program_id'], ['program_id'])
        result = dict((data['program_id'][0], data['program_id_count']) for data in lead_data)
        for program in self:
            program.opportunity_count = result.get(program.id, 0)
            
    def _compute_project_count(self):
        project_data = self.env['project.project'].read_group([('program_id', 'in', self.ids), ('parent_id', '=', False)], ['program_id'], ['program_id'])
        result = dict((data['program_id'][0], data['program_id_count']) for data in project_data)
        for program in self:
            program.project_count = result.get(program.id, 0)
    
    @api.multi
    def action_projects_followup(self):
        self.ensure_one()
        action = self.env.ref('vcls-timesheet.project_timesheet_forecast_report_action').read()[0]
        project_ids = self.env['project.project'].search([('program_id','=',self.id)]).mapped('id')
        action['context'] = { 
                "search_default_project_id": project_ids,
                }
        return action


### ADD PROGRAM TO OTHER MODELS ###
class Client(models.Model):

    _inherit = 'res.partner'

    program_ids = fields.One2many(
        'project.program',
        'client_id',
        string = 'Client Programs',
        readonly = True,
    )

    program_count = fields.Integer(
        compute = '_compute_program_count',
    )

    ### METHODS ###
    @api.depends('program_ids')
    def _compute_program_count(self):
        for client in self:
            client.program_count = len(client.program_ids)

class Lead(models.Model):

    _inherit = 'crm.lead'

    program_id = fields.Many2one(
        comodel_name = 'project.program',
        string = 'Related Program',
    )

    app_country_group_id = fields.Many2one(
        'res.country.group',
        string = "Application Geographic Area",
        related = 'program_id.app_country_group_id',
        readonly = True
    )

    client_product_ids = fields.Many2many(
        'client.product',
        string = 'Client Product',
        related = 'program_id.client_product_ids',
        readonly = True
    )

    """therapeutic_area_ids = fields.Many2many(
        'therapeutic.area',
        string ='Therapeutic Area',
        related = 'program_id.therapeutic_area_ids',
        readonly = True
    )
    
    targeted_indication_ids = fields.Many2many(
        'targeted.indication',
        string ='Targeted Indication',
        related = 'program_id.targeted_indication_ids',
        readonly = True)"""
    

    program_stage_id = fields.Selection([
        ('pre', 'Preclinical'),
        ('exploratory', 'Exploratory Clinical'),
        ('confirmatory', 'Confirmatory Clinical'),
        ('post', 'Post Marketing')],
        'Program Stage',
        related='program_id.stage_id',
        readonly=True,)
    
    product_name = fields.Char(
        string = "Product Name",
        help = 'The client product name',
        related='program_id.product_name',
    )

    product_description = fields.Char(
        related="program_id.product_description",
    )

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    program_id = fields.Many2one(
        comodel_name = 'project.program',
        string = 'Related Program',
    )    

class Project(models.Model):

    _inherit = 'project.project'

    program_id = fields.Many2one(
        comodel_name = 'project.program',
        string = 'Related Program',
    )