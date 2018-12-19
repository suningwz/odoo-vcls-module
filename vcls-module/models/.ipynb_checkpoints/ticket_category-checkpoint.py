# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class WizardTicket(models.TransientModel):
    _name = 'wizard.ticket'
    
    message = fields.Text('Message')
    ticket_id = fields.Many2one('helpdesk.ticket', 'Ticket')
    
    @api.multi
    def set_to_progess(self):
        self.ensure_one()
        progress_stage = self.env.ref('helpdesk.stage_in_progress')
        self.ticket_id.stage_id = progress_stage
        self.ticket_id.message_post(body=self.message)


class Ticket(models.Model):
    
    _inherit = 'helpdesk.ticket'
    
    ###################
    # Default Methods #
    ###################
    @api.model
    def _get_partner_id(self):
        user = self.env['res.users'].browse(self._uid)
        return user.partner_id
    
    @api.model
    def _get_type_id(self):
        return self.env.ref('vcls-module.ticket_type_incident').id
    
    #################
    # Custom Fields #
    #################
    
    subcategory_id = fields.Many2one(
        'helpdesk.ticket.subcategory',
        string='Subcategory',
        required=True,)
    
    #overrides for renaming purpose
    name = fields.Char(
        compute='_get_name',
        reverse='_set_name',)
    
    display_name = fields.Char(
        compute='_get_name',)
    
    team_id = fields.Many2one(
        string="Category",
        default=False,
        required=True)
    
    partner_id = fields.Many2one(
        string="Requester",
        default=_get_partner_id,)
    
    partner_name = fields.Char(
        string="Requester Name",)
    
    partner_email = fields.Char(
        string="Email",)
    
    ticket_type_id =fields.Many2one()
    
    #used for dynamic views
    access_level = fields.Selection([ 
        ('base', 'Base'),
        ('support', 'Support'),
    ], compute='_get_access_level', store=False)
    
    set_to_progress_visible = fields.Boolean(compute='_get_set_to_progress_visible', store=False)
    
    @api.depends('stage_id')
    def _get_set_to_progress_visible(self):
        awaiting_stage = self.env.ref('__export__.helpdesk_stage_9_1ddd697e')
        for ticket in self:
            ticket.set_to_progress_visible = (ticket.stage_id == awaiting_stage) 
    
    @api.multi
    def open_wizard_set_in_progress(self):
        self.ensure_one()
        
        wiz = self.env['wizard.ticket'].create({
            'ticket_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Set in Progress',
            'view_mode': 'form',
            'res_model': 'wizard.ticket',
            'res_id': wiz.id,
            'target': 'new',
        }
    
    #################################
    # Automated Calculation Methods #
    #################################
    
    @api.multi
    def _get_access_level(self):
        for rec in self:
            user = self.env['res.users'].browse(self._uid)
            if user.has_group('helpdesk.group_helpdesk_user'):
                rec.access_level = 'support'
            else:
                rec.access_level = 'base'
    
    @api.depends('team_id','subcategory_id')
    def _get_name(self):
        for ticket in self:
            if ticket.team_id:
                try:
                    ticket.name = "{:06} | {}".format(ticket.id,ticket.team_id.name)
                except:
                    ticket.name = "{}".format(ticket.team_id.name)
            if ticket.subcategory_id:
                ticket.name = "{} - {}".format(ticket.name,ticket.subcategory_id.name)
            ticket.display_name = ticket.name
    
    @api.onchange('name')
    def _set_name(self):
        for ticket in self: pass
             
    @api.onchange('team_id')
    def _onchange_team_id(self):
        for ticket in self:
            ticket.subcategory_id = False
    
    '''
    category_id = fields.Many2one(
        'helpdesk.ticket.category',
        string='Category',)
        
    employee_id = fields.Many2one(
        'hr.employee',
        string='Requester',)
    
    priority = fields.Selection(
        default='0',)
        
    
    
    
    user_id = fields.Many2one(
        compute='_get_assignment',
        inverse='_set_assignment',)
    
    
    #used to store manually assigned teams or user
    manual_team_id = fields.Many2one(
        'helpdesk.team',)
    
    manual_user_id = fields.Many2one(
        'res.user',)
    
    
    
    @api.onchange('team_id','user_id')
    def _set_assignment(self): #store the manually entered value
        for ticket in self:
            ticket.manual_team_id = ticket.team_id
            ticket.manual_user_id = ticket.user_id
    
    @api.onchange('category_id','subcategory_id','employee_id')
    def _set_manual_assignment(self):
        for ticket in self:
            ticket.manual_team_id = ticket._get_route(ticket.category_id, ticket.subcategory_id,ticket.employee_id.office_id)
            ticket.manual_user_id = False
            
    
    @api.depends('category_id','subcategory_id','employee_id','manual_team_id','manual_user_id')
    def _get_assignment(self):
        for ticket in self:
            ticket.team_id = ticket.manual_team_id
            ticket.user_id = ticket.manual_user_id
    
    
        
    ################
    # Tool Methods #
    ################
    
    def _get_route(self,category_id=False,subcategory_id=False,office_id=False):
         return False
    '''

class TicketCategory(models.Model):
    
    _name = 'helpdesk.ticket.category'
    _description = 'Ticket Category'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char()
    
class TicketSubCategory(models.Model):
    
    _name = 'helpdesk.ticket.subcategory'
    _description = 'Ticket SubCategory'
    _order = 'name'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char()
    
    team_id = fields.Many2one(
        'helpdesk.team',
        string='Category',)
    
class TicketRoute(models.Model):
    
    _name = 'helpdesk.ticket.route'
    _description = 'Ticket Route'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char()
    
    subcategory_id = fields.Many2one(
        'helpdesk.ticket.subcategory',
        string='Subategory',)
    
    office_id = fields.Many2one(
        'hr.office',
        string='Office',)
    
    assignee_id = fields.Many2one(
        'res.users',
        string='Assigned to',)