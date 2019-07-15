# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.forecast'

    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True, readonly=True)