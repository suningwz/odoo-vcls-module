# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class Contact(models.Model):
    _inherit='res.partner'

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
