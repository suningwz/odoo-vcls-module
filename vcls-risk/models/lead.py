from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class Leads(models.Model):

    _inherit = 'crm.lead'

    risk_raised = fields.Boolean(default = False)

    def raise_go_nogo(self):
        for record in self:
            self.env['risk']._raise_risk(self.env.ref('vcls-risk.risk_go_nogo'), 'Approval required for {}'.format(record.name))
            record.risk_raised = True