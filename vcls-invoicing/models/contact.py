# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class Contact(models.Model):
    _inherit = 'res.partner'
    risk_ids = fields.Many2many('risk', string='Risk')

    communication_rate = fields.Selection([ (0.0, '0%'), 
                                            (0.05, '0.5%'), 
                                            (0.1, '1%'), 
                                            (0.15, '1.5%'), 
                                            (0.2, '2%'), 
                                            (0.25, '2.5%'), 
                                            (0.3, '3%'), 
                                            ], 'Communication Rate', default = 0.0)
    
    invoicing_frequency = fields.Selection([('month','Month'),
                                            ('trimester','Trimester'),
                                            ('milestone','Miliestone')], default='month')
    
    outsourcing_permission = fields.Boolean(default=False)

    invoice_template = fields.Many2one('ir.actions.report', domain=[('model','=','account.invoice')])

    activity_report_template = fields.Many2one('ir.actions.report', domain=[('model','=','account.analytic.line'), ('report_name','=','activity_report')])

    def action_risk(self):
        view_ids = [self.env.ref('vcls-risk.view_risk_tree').id,
                    self.env.ref('vcls-risk.view_risk_kanban').id, 
                    self.env.ref('vcls-risk.view_risk_form').id ]
        risk_ids = self.risk_ids

        return {
            'name': 'All Risks',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form',
            'view_ids': view_ids,
            'target': 'current',
            'res_model': 'risk',
            'type': 'ir.actions.act_window',
            'context': {'search_default_id': risk_ids.ids,},
        } 

    def action_po(self):
        po_ids = self.env['invoicing.po'].search([('partner_id','=',self.id)]).ids

        return {
            'name': 'Purchase Order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'invoicing.po',
            'type': 'ir.actions.act_window',
            'context': {"default_id": po_ids, 
                "search_default_id": [po_ids], },
        } 