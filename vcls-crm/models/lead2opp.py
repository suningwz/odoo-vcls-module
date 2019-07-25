from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError, Warning

class Lead2OpportunityPartner(models.TransientModel):

    # Replace only label for name
    _inherit = 'crm.lead2opportunity.partner'

    name = fields.Selection([
        ('convert', 'Convert to new opportunity'),
        ('merge', 'Merge with existing opportunity')
    ], 'Conversion Action', required=True)
