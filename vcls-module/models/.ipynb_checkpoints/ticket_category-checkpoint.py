# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class Ticket(models.Model):
    
    _inherit = 'helpdesk.ticket'
    
    #################
    # Custom Fields #
    #################
    
    category_id = fields.Many2one(
        'helpdesk.ticket.category',
        string='Category',)
    
    subcategory_id = fields.Many2one(
        'helpdesk.ticket.subcategory',
        string='Subcategory',)
    
    
    '''
    employee_id = fields.Many2one(
        'hr.employee',
        string='Requester',)
    
    priority = fields.Selection(
        default='0',)
        
    team_id = fields.Many2one(
        compute='_get_assignment',
        inverse='_set_assignment',)
    
    
    user_id = fields.Many2one(
        compute='_get_assignment',
        inverse='_set_assignment',)
    '''
    
    #used to store manually assigned teams or user
    manual_team_id = fields.Many2one(
        'helpdesk.team',)
    
    manual_user_id = fields.Many2one(
        'res.user',)
    
    #################################
    # Automated Calculation Methods #
    #################################
    '''
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
    
    '''
        
    ################
    # Tool Methods #
    ################
    
    def _get_route(self,category_id=False,subcategory_id=False,office_id=False):
         return False

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
    
    category_id = fields.Many2one(
        'helpdesk.ticket.category',
        string='Category',)
    
class TicketRoute(models.Model):
    
    _name = 'helpdesk.ticket.route'
    _description = 'Ticket Route'
    
    #################
    # Custom Fields #
    #################
    
    name = fields.Char()
    
    category_id = fields.Many2one(
        'helpdesk.ticket.category',
        string='Category',)
        
    subcategory_id = fields.Many2one(
        'helpdesk.ticket.subcategory',
        string='Subategory',)
    
    office_id = fields.Many2one(
        'hr.office',
        string='Office',)
    
    team_id = fields.Many2one(
        'helpdesk.team',
        string='Assigned Team',)