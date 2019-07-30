from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError, Warning

class Lead2OpportunityPartner(models.TransientModel):

    # Replace only label for name
    _inherit = 'crm.lead2opportunity.partner'

    name = fields.Selection([
        ('convert', 'Convert to new opportunity'),
        ('merge', 'Merge with existing opportunity')
    ], 'Conversion Action', required=True)

    opp_name = fields.Char(string = 'Opportunity Name', default =lambda self: self._get_lead_name())

    @api.model
    def _get_lead_name(self):
        return self.env['crm.lead'].browse(self._context['active_id']).name
    '''
    @api.multi
    def action_apply(self):
        self.env['crm.lead'].browse(self._context['active_id']).name = self.opp_name
        return super(Lead2OpportunityPartner, self).action_apply()
'''
