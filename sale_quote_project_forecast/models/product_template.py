from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    forecast_employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Forecast employee",
    )
    seniority_level_id = fields.Many2one(
        name='Seniority level',
        comodel_name='hr.employee.seniority.level',
        ondelete='restrict',
    )
