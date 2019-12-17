# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class ProjectSummary(models.Model):
    _name = 'project.summary'
    _order = "create_date desc"
    _description = 'Project Summary'

    project_id = fields.Many2one(
        'project.project',
        'Project',  readonly=True
    )
    internal_summary = fields.Html(
        'Internal summary'
    )
    external_summary = fields.Html(
        'External summary'
    )
    completion_ratio = fields.Float('Task Complete')
    consumed_value = fields.Float('Budget Consumed')
    consumed_completed_ratio = fields.Float('Budget Consumed/Task Complete')

    @api.multi
    def name_get(self):
        return [(summary.id, '%s-%s' %
                 (summary.id, fields.Datetime.to_string(summary.create_date)))
                for summary in self]

    @api.one
    @api.constrains('internal_summary')
    def _check_internal_summary(self):
        if self.internal_summary == '<p><br></p>':
            raise ValidationError(_('Please set an internal summary'))


