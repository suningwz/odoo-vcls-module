# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class Ticket(models.Model):
    
    _inherit = 'helpdesk.ticket'
    
    ###################
    # Default Methods #
    ###################
    @api.model
    def _get_partner_id(self):
        user = self.env['res.users'].browse(self._uid)
        return user.partner_id
    
    #################
    # Custom Fields #
    #################
    
    subcategory_id = fields.Many2one(
        'helpdesk.ticket.subcategory',
        string='Subcategory',)
    
    #overrides for renaming purpose
    name = fields.Char(
        compute='_get_name',
        reverse='_set_name',)
    
    team_id = fields.Many2one(
        string="Category",
        default=False,)
    
    partner_id = fields.Many2one(
        string="Requester",
        default=_get_partner_id,)
    
    partner_name = fields.Char(
        string="Requester Name",)
    
    partner_email = fields.Char(
        string="Email",)
    
    #used for dynamic views
    access_level = fields.Selection([ 
        ('base', 'Base'),
        ('support', 'Support'),
    ], compute='_get_access_level', store=False)
    
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
    
    @api.depends('ticket_type_id','team_id','subcategory_id')
    def _get_name(self):
        for ticket in self:
            if ticket.ticket_type_id:
                ticket.name = "{}".format(ticket.ticket_type_id.name)
            if ticket.team_id:
                ticket.name = "{} | {}".format(ticket.name,ticket.team_id.name)
            if ticket.subcategory_id:
                ticket.name = "{} - {}".format(ticket.name,ticket.subcategory_id.name)
    
    @api.onchange('name')
    def _set_name(self):
        for ticket in self: pass
                
    
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