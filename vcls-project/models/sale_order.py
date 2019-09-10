from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):

    _inherit = 'sale.order'
    
    child_ids = fields.One2many('sale.order', 'parent_id', string='Childs orders')
    
    @api.multi
    def quotation_program_print(self):
        """ Print all quotation related to the program
        """
        programs = self.mapped('program_id')
        quot = self.search([('program_id', 'in', programs.ids), ('state', '=', 'draft')])
        return self.env.ref('sale.action_report_saleorder').report_action(quot)

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
