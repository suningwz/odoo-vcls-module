from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    """def contact_book(self):
        view_id = self.env.ref('vcls-project.view_project_form_contact_book').id
        return {
            'name': 'Project Contact Book',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_model': 'project.project',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
        }"""
