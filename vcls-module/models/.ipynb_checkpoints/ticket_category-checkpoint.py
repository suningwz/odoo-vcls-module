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