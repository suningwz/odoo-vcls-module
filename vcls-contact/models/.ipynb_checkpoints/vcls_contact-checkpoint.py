# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContactExt(models.Model):
    
    _inherit = 'res.partner'

    
    hidden = fields.Boolean(string="Confidential", default=False)
# class vcls-contact(models.Model):
#     _name = 'vcls-contact.vcls-contact'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100