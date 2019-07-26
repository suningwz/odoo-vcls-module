# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    forecast_employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Forecast employee",
    )
