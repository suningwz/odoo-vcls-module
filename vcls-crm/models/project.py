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
