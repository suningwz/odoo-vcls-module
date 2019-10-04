# -*- coding: utf-8 -*-
####################################################################
#
# © 2018-Today Somko Consulting (<https://www.somko.be>)
#
# License OPL-1 or later (https://www.odoo.com/documentation/user/11.0/legal/licenses/licenses.html)
#
####################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aad_contact_sync_direction = fields.Selection(string='Contact Sync Direction', related='company_id.aad_contact_sync_direction', readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    aad_contact_sync_direction = fields.Selection(string='Office Contact Sync Direction', required=True, default='both', selection=[
        # ('a2o', 'Office365 to Odoo'),
        ('o2a', 'Odoo to Office365'),
        ('both', 'Mirror'),
    ])
