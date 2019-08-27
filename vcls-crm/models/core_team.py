# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class CoreTeam(models.Model):

    _name = 'core.team'
    _description = 'Link teams to quotations & projects'
    
    lead_consultant = fields.Many2one(
        'hr.employee',
        string='Lead Consultant',
       )

    consultant_ids = fields.Many2many(
        'hr.employee',
        string='Consultants')

    ta_ids = fields.Many2many(
        'hr.employee',
        string='Ta')
    
    comment = fields.Char()
    
class SaleOrder(models.Model):

    _inherit = 'sale.order'

    core_team_id = fields.Many2one(
        'core.team',
        string = "Core Team"
    )

    def core_team(self):
        view_id = self.env.ref('vcls-crm.view_core_team_form').id

        if not self.core_team_id: #if core team not defined by parent, then we create a default one
            self.core_team_id = self.env['core.team'].create({})

        return {
            'name': 'Core Team',
            'view_type': 'form',
            'view_mode': 'form',
            'target': self.core_team_id,
            'res_model': 'core.team',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
        }

class Project(models.Model):

    _inherit = 'project.project'

    core_team_id = fields.Many2one(
        'core.team',
        related = "sale_order_id.core_team_id"
    )