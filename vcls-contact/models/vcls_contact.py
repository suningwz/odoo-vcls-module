# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContactExt(models.Model):

    _inherit = 'res.partner'
    
    ### CUSTOM FIELDS FOR EVERY KIND OF CONTACTS ###

    hidden = fields.Boolean(
        string="Confidential",
        default=False,
    )

    is_internal = fields.Boolean(
        string="Is Internal",
        compute = '_compute_is_internal',
        store = True,
        default = False,
    )

    stage = fields.Selection([
        ('1', 'Undefined'),
        ('2', 'New'),
        ('3', 'Verified'),
        ('4', 'Outdated'),
        ('5', 'Archived')], 
        string='Status',
        default='1',
    )

    ### CLIENT RELATED FIELDS ###

    ###################
    # COMPUTE METHODS #
    ###################
    
    @api.depends('employee')
    def _compute_is_internal(self):
        for contact in self:
            if contact.employee or self.env['res.company'].search([('partner_id.id','=',contact.id)]):
                contact.is_internal = True

    # We reset the number of bounced emails to 0 in order to re-detect problems after email change
    @api.onchange('email')
    def _reset_bounce(self):
        for contact in self:
            contact.message_bounce = 0