# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api


class ResUsers(models.Model):

    _inherit = 'res.users'

    project_ids = fields.One2many(
        'project.project', 'user_id'
    )
