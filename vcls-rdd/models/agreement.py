# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api


class Agreement(models.Model):
    _inherit = 'agreement'

    @api.model
    def _get_rdd_name(self, vals):
        partner = self.env['res.partner'].browse(vals.get('partner_id'))
        name = partner.name
        agreement_type_id = vals.get('agreement_type_id')
        start_date = vals.get('start_date')
        if agreement_type_id == 1:
            name = '.'.join([name, 'agreement'])
        elif agreement_type_id == 13:
            name = '.'.join([name, 'CDA'])
        elif agreement_type_id == 10:
            name = '.'.join([name, 'MECA'])
        if start_date:
            name = '_'.join([name, start_date])
        if vals.get('end_date'):
            name = '_'.join([name, vals.get('end_date')])
        vals['name'] = name
        if agreement_type_id == 10 and start_date:
            vals['end_date'] = fields.Date.to_string(
                fields.Date.from_string(start_date) + relativedelta(
                    years=2))
        return vals

    @api.model
    def create(self, vals):
        if self.env.user.context_data_integration and not vals.get('name'):
            vals = self._get_rdd_name(vals)
        return super(Agreement, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.env.user.context_data_integration and not vals.get('name'):
            vals = self._get_rdd_name(vals)
        return super(Agreement, self).write(vals)
