# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    old_id = fields.Char("Old Id", copy=False, readonly=True)

    @api.multi
    def write(self, vals):
        if isinstance(vals.get('time_category_ids'), int) and \
                self.env.user.context_data_integration:
            vals['time_category_ids'] = [(4, vals['time_category_ids'])]
        return super(ProjectTask, self).write(vals)


class ProjectTimeCategory(models.Model):
    _inherit = 'project.time_category'

    old_id = fields.Char("Old Id", copy=False, readonly=True)

