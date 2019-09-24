# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default='',
                                 help="Company related to this journal")


# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     def get_company_id(self):
#         import ipdb; ipdb.set_trace()
#         if self._context.get('params', False):
#             move = self.env['account.move'].browse(self._context.get('params')['id'])
#         return True

