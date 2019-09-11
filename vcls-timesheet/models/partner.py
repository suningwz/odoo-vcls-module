# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models, fields


class ContactExt(models.Model):
    _inherit = 'res.partner'

    controller_id = fields.Many2one(
        domain=lambda self: [("groups_id", "=",
                              self.env.ref('vcls-timesheet.vcls_pc').id)]
    )