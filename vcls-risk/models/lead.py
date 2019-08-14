from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class Leads(models.Model):

    _inherit = 'crm.lead'

    risk_raised = fields.Boolean(default = False)

    def raise_go_nogo(self):
        for record in self:
            self.env['risk']._raise_risk(self.env.ref('vcls-risk.risk_go_nogo'), '{},{}'.format(record._name, record.id))
            record.risk_raised = True
    
    def open_related_risks(self):
        return {
            'name': 'All related risk(s)',
            'view_mode': 'tree',
            'target': 'new',
            'res_model': 'risk',
            'type': 'ir.actions.act_window',
            'domain': "[('resource','=', '{},{}')]".format(self._name, self.id)
        }