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
    
    lead_backup = fields.Many2one(
        'hr.employee',
        string='Lead Consultant Backup',
       )

    consultant_ids = fields.Many2many(
        'hr.employee',
        string='Consultants')

    ta_ids = fields.Many2many(
        'hr.employee',
        string='Ta')
    
    comment = fields.Char()

    @api.onchange('lead_consultant')
    def _onchange_lc(self):
        #we look for projects having the related core team, and we update the project manager
        for team in self:
            projects = self.env['project.project'].search([('core_team_id','=',team)])
            _logger.info("Projects {} for Core Team {}".format(projects.mapped('name'),team.id))
            if projects:
                projects.write({'user_id':team.lead_consultant.user_id.id})
    
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
                rec.core_team_id = rec.env['core.team'].create({'name':"Team {}".format(rec.internal_ref)})
                #rec.write({'core_team_id':team})
                #_logger.info("{} | {}".format(team.name, rec.core_team_id.name))

            return {
                'name': 'Core Team',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': rec.core_team_id.id,
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