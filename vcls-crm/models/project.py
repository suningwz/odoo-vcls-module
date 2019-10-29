# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class Project(models.Model):

    _inherit = 'project.project'

    core_team_id = fields.Many2one(
        'core.team',
        related="sale_order_id.core_team_id"
    )

    def core_team(self):
        view_id = self.env.ref('vcls-crm.view_core_team_form').id

        for rec in self:
            # if core team not defined by parent, then we create a default one
            if not rec.core_team_id:
                # use sudo as Lead consultant cannot write on sales orders
                rec.sudo().core_team_id = self.env['core.team'].create({'name': "Team {}".format(rec.internal_ref)})

            return {
                'name': 'Core Team',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': rec.core_team_id.id,
                'res_model': 'core.team',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
            }
