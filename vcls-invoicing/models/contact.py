# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class Contact(models.Model):
    _inherit = 'res.partner'
    risk_ids = fields.Many2many('risk', string='Risk')

    communication_rate = fields.Selection([ ('0.0', '0%'), 
                                            ('0.005', '0.5%'), 
                                            ('0.01', '1%'), 
                                            ('0.015', '1.5%'), 
                                            ('0.02', '2%'), 
                                            ('0.025', '2.5%'), 
                                            ('0.03', '3%'), 
                                            ], 'Communication Rate', default = '0.0')
    
    invoicing_frequency = fields.Selection([('month','Month'),
                                            ('trimester','Trimester'),
                                            ('milestone','Milestone')], default='month')
    
    outsourcing_permission = fields.Boolean(default=False)

    def get_default_invoice_template(self):
        return self.env['ir.action.report'].search([('model', '=', 'account.invoice'),('name', 'ilike', 'invoice simple')],limit=1)

    invoice_template = fields.Many2one(
        'ir.actions.report', 
        domain=[('model', '=', 'account.invoice'),('name', 'ilike', 'invoice')],
        default = _get_default_invoice_template,
        )

    activity_report_template = fields.Many2one('ir.actions.report', domain=[('model', '=', 'account.invoice'),('name', 'ilike', 'activity')])

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