# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, http

from odoo.exceptions import UserError, ValidationError

class MailActivity(models.Model):
    
    _inherit = 'mail.activity'

    lm_ids = fields.Many2many(
        'res.users',
        compute='_get_lm_ids',
        default = False,
        store = True,
    )

    @api.depends('user_id')  
    def _get_lm_ids(self):
        """ Populate a list of authorized user for domain filtering 
        for rec in self:
            empl = self.env['hr.employee'].search([('user_id','=',rec.user_id.id)])
            if empl:
                rec.write({'lm_ids':[(6,0,empl.lm_ids.mapped('id'))]})
        """
        return False

    def go_to_record(self):
        self.ensure_one()
        url = http.request.env['ir.config_parameter'].get_param('web.base.url')
        link = "{}/web#id={}&model={}".format(url, self.res_id, self.res_model)
        return {
            'type': 'ir.actions.act_url',
            'url': link,
            'target': 'current',
        }
