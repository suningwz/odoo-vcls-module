# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class CoreTeam(models.Model):

    _name = 'core.team'
    _description = 'Core Team'

    name = fields.Char()
    
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

        for rec in self:
            if not rec.core_team_id: #if core team not defined by parent, then we create a default one
                team = rec.env['core.team'].create({'name':"Team {}".format(rec.internal_ref)})
                #rec.write({'core_team_id':team})
                rec.core_team_id = team
                _logger.info("{} | {}".format(team.name, rec.core_team_id.name))
            else:
                team = rec.core_team_id


        return {
            'name': 'Core Team',
            'view_type': 'form',
            'view_mode': 'form',
            'target': team,
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