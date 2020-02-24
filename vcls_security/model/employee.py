# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)

class Employee(models.Model):
    _inherit = 'hr.employee'

    #adds or remove from the lm group according to the subortinates count
    @api.model #to be called from CRON job
    def _check_lc_membership(self):
        #c_group = self.env.ref('vcls_security.group_vcls_consultant')
        lc_group = self.env.ref('vcls_security.vcls_lc')
        sup_group = self.env.ref('vcls-hr.vcls_group_superuser_lvl1')

        effective_lc_ids = self.env['project.project'].search([('project_type','=','client')]).mapped('user_id')

        users_to_upgrade = ((effective_lc_ids | sup_group.users) - lc_group.users).filtered(lambda p: p.active)
        users_to_downgrade = (lc_group.users - (effective_lc_ids | sup_group.users)).filtered(lambda p: p.active)

        _logger.info("LC MEMBERSHIP TO UPGRADE: {}\nLC MEMBERSHIP TO DOWNGRADE: {}".format(users_to_upgrade.mapped('name'),users_to_downgrade.mapped('name')))

        users_to_upgrade.write({'groups_id': [(4, lc_group.id)]}) 
        users_to_downgrade.write({'groups_id': [(3, lc_group.id)]})
