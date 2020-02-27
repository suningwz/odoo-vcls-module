from odoo import models, fields, api
from datetime import datetime

class KpiType(models.Model):
    _name = 'kpi.type'
    _description = 'Kpi Type'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    owning_group_id = fields.Many2one(
        comodel_name='res.groups',
        string='Owning group'
    )

class Kpi(models.Model):
    _name = 'kpi.kpi'
    _description = 'Kpi'

    type_id = fields.Many2one(
        comodel_name='kpi.type',
        string='Kpi Type',
        required=True
    )
    source_model = fields.Char(string='Model', required=True)
    source_id = fields.Integer(required=True)
    activity_create_date = fields.Datetime(required=True)
    activity_create_uid = fields.Many2one(
        comodel_name='res.users',
        string='Created by'
    )
    activity_close_date = fields.Datetime(required=True)
    activity_close_uid = fields.Many2one(
        comodel_name='res.users',
        string='Closed by',
        required=True
    )
    value = fields.Char()
    description = fields.Char()

class MailActivityTypeInherit(models.Model):
    _inherit = 'mail.activity.type'

    kpi_type_id = fields.Many2one(
        comodel_name='kpi.type',
        string='Kpi Type'
    )

class MailActivityInherit(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    def action_feedback(self, feedback=False):
        for m in self:
            if m.activity_type_id.kpi_type_id:
                self.env['kpi.kpi'].create({
                    'type_id': m.activity_type_id.kpi_type_id.id,
                    'source_model': m.res_model,
                    'source_id': m.res_id,
                    'activity_create_date': m.create_date,
                    'activity_create_uid': m.create_uid.id,
                    'activity_close_date': datetime.now(),
                    'activity_close_uid': self.env.user.id,
                    'description': m.summary,
                })
        return super().action_feedback(feedback)
