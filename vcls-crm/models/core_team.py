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
    
    assistant_id = fields.Many2one(
        comodel_name='hr.employee',
        string = 'project.assistant',
        compute = '_compute_assistant_id',
        store = True,
    )

    consultant_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='rel_table_core_team_consultants',
        string='Consultants')

    ta_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='rel_table_core_team_tas',
        string='Ta')
    
    comment = fields.Char()
    user_ids = fields.Many2many('res.users', store=True, compute='compute_core_team_related_users_list')
    project_ids = fields.One2many(
        'project.project',
        'core_team_id'
    )

    @api.multi
    def write(self, vals):
        if vals.get('lead_consultant',False):
            lc_user = self.env['hr.employee'].browse(vals.get('lead_consultant')).user_id

            #we look for projects having the related core team, and we update the project manager
            for team in self:
                projects = self.env['project.project'].search([('core_team_id','=',team.id)])
                _logger.info("Updated Projects {} for Core Team {}".format(projects.mapped('name'),team.name))
                if projects:
                    projects.write({'user_id':lc_user.id})

        return super(CoreTeam, self).write(vals)

    @api.depends('project_ids.partner_id.assistant_id')
    def _compute_assistant_id(self):
        for team in self:
            if team.project_ids:
                if team.project_ids[0].partner_id:
                    if team.project_ids[0].partner_id.assistant_id:
                        assistant = self.env['hr.employee'].search([('user_id','=',team.project_ids[0].partner_id.assistant_id.id)],limit=1)
                        if assistant:
                            team.assistant_id = assistant

    
    @api.depends('lead_consultant', 'lead_backup', 'ta_ids', 'consultant_ids','assistant_id')
    def compute_core_team_related_users_list(self):
        for team in self:
            team.user_ids = (team.consultant_ids | team.ta_ids |
                            team.lead_backup | team.assistant_id |
                            team.lead_consultant).mapped('user_id')


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    core_team_id = fields.Many2one(
        'core.team',
        string="Core Team"
    )

    def core_team(self):
        self.ensure_one()
        view_id = self.env.ref('vcls-crm.view_core_team_form').id
        # if core team not defined by parent, then we create a default one
        if not self.core_team_id:
            # use sudo as Lead consultant cannot write on sales orders
            self.sudo().core_team_id = self.env['core.team'].sudo().create({'name': "Team {}".format(self.internal_ref)})

        return {
            'name': 'Core Team',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.core_team_id.id,
            'res_model': 'core.team',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
        }
