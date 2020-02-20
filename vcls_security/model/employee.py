# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.osv import expression


class Employee(models.Model):
    _inherit = 'hr.employee'

    #adds or remove from the lm group according to the subortinates count
    @api.model #to be called from CRON job
    def _check_lc_membership(self):
        group = self.env.ref('vcls_security.vcls_lc')
        lc_ids = self.env['project.project'].search([]).mapped('user_id')
        non_lc_ids = self.env['res.users'].search([('sel_groups_1_9_10','=',1),('id','not in',lc_ids)])

        lc_ids.write({'groups_id': [(4, group.id)]}) 
        non_lc_ids.write({'groups_id': [(3, group.id)]}) 

