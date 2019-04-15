# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContactExt(models.Model):

    _inherit = 'res.partner'

    hidden = fields.Boolean(
        string="Confidential",
        default=False,
        )

    stage = fields.Selection([
        ('1', 'Undefined'),
        ('2', 'New'),
        ('3', 'Verified'),
        ('4', 'Outdated'),
        ('5', 'Archived'),], 
        string='Status',
        track_visibility='onchange',
        default='1',
        )

    is_internal = fields.Boolean(
        string="Is Internal",
        compute = '_compute_is_internal',
        store = True,
        default = False,
    )

    ###################
    # COMPUTE METHODS #
    ###################
    
    @api.depends('employee')
    def _compute_is_internal(self):
        for contact in self:
            if contact.employee or self.env['res.company'].search([('partner_id.id','=',contact.id)]):
                contact.is_internal = True