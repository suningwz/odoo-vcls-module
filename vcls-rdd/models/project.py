# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    old_id = fields.Char("Old Id", copy=False, readonly=True)
