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

    program_info = fields.Text(
        compute = '_compute_program_info',
        store = True,
    )

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
    
    product_description = fields.Text()
    
    sale_order_count = fields.Integer(compute='_compute_sale_order_count', string='Sale Order Count')
    opportunity_count = fields.Integer(compute='_compute_opportunity_count', string='Opportunity Count')
    project_count = fields.Integer(compute='_compute_project_count', string='Main Project Count')
    invoice_count = fields.Integer(compute='_compute_invoice_count', string='Invoice Count')

    @api.depends('name','product_name','client_id','leader_id','app_country_group_id',
                   'prim_therapeutic_area_id','prim_indication_id','prim_detailed_indication',
                   'sec_therapeutic_area_id','sec_indication_id','sec_detailed_indication', )
    def _compute_program_info(self):
        for program in self:
            info = "{} Program | {} for {} in {} \nled by {}:\n\n".format(program.client_id.name,program.name,program.product_name,program.app_country_group_id.name,program.leader_id.name)
            if program.prim_therapeutic_area_id:
                info += "Primary Therapeutic Info:\nArea | {}\nIndication | {}\nDetails | {}\n\n".format(program.prim_therapeutic_area_id.name,program.prim_indication_id.name,program.prim_detailed_indication)
            if program.sec_therapeutic_area_id:
                info += "Secondary Therapeutic Info:\nArea | {}\nIndication | {}\nDetails | {}\n\n".format(program.sec_therapeutic_area_id.name,program.sec_indication_id.name,program.sec_detailed_indication)
            program.program_info = info

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
    
    def _compute_invoice_count(self):
        for program in self:
            program.invoice_count = sum(self.env['project.project'].search([('program_id','=',program.id)]).mapped('invoices_count'))
    
    @api.multi
    def action_projects_followup(self):
        self.ensure_one()
        action = self.env.ref('vcls-timesheet.project_timesheet_forecast_report_action').read()[0]
        project_ids = self.env['project.project'].search([('program_id','=',self.id)]).mapped('id')
        action['context'] = { 
                "search_default_project_id": project_ids,
                }
        return action
    
    @api.multi
    def action_open_invoices(self):
        self.ensure_one()
        action = self.env.ref('vcls-invoicing.action_ia_invoices').read()[0]
        invoice_ids = self.env['project.project'].search([('program_id','=',self.id)]).mapped('out_invoice_ids.id')
        action['context'] = { 
                "search_default_invoice_id": invoice_ids,
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

    """client_product_ids = fields.Many2many(
        'client.product',
        string = 'Client Product',
        related = 'program_id.client_product_ids',
        readonly = True
    )"""

    program_stage_id = fields.Selection([
        ('pre', 'Preclinical'),
        ('exploratory', 'Exploratory Clinical'),
        ('confirmatory', 'Confirmatory Clinical'),
        ('post', 'Post Marketing')],
        string='Program Stage',
        #related='program_id.stage_id',
        #readonly=True,
        )
    
    product_name = fields.Char(
        string = "Product Name",
        help = 'The client product name',
        related='program_id.product_name',
    )

    product_description = fields.Text(
        related="program_id.product_description",
    )

    program_info = fields.Text(
        related = 'program_id.program_info'
    )

    @api.onchange('program_id')
    def _onchange_program_id(self):
        self.program_stage_id = self.program_id.stage_id

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