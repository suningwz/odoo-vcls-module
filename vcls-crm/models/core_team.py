# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class CoreTeam(models.Model):

    _name = 'core.team'
    _description = 'Link teams to quotations & projects'
    
    lead_consultant = fields.Many2one(
        'hr.employee',
        string='Lead Consultant',
        required = True,
       )

    consultant_ids = fields.Many2many(
        'hr.employee',
        string='Consultants')
    ta_ids = fields.Many2many(
        'hr.employee',
        string='Ta')
    
class SaleOrder(models.Model):

    _inherit = 'sale.order'

    core_team_id = fields.Many2one(
        'core.team',
        string = "Core Team"
    )

class Project(models.Model):

    _inherit = 'project.project'

    core_team_id = fields.Many2one(
        'core.team',
        related = "sale_order_id.core_team_id"
    )