# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    ####################
    # OVERRIDEN FIELDS #
    ####################

    company_id = fields.Many2one(
        string = 'Trading Entity',
        default = lambda self: self.env.ref('vcls-hr.company_VCFR'),
        )

    #################
    # CUSTOM FIELDS #
    #################

    expertise_id = fields.Many2one(
        'expertise.area',
        string="Area of Expertise",
    )

    deliverable_ids = fields.Many2many(
        'product.deliverables',
    )

    access_level = fields.Selection([
        ('rm', 'Resource Manager'),
        ('lc', 'Lead Consultant'),], 
        compute='_get_access_level',
        store=False,
        default='lc',)

    ###################
    # COMPUTE METHODS #
    ###################

    @api.multi
    def _get_access_level(self):
        user = self.env['res.users'].browse(self._uid)

        for rec in self:           
            #if rm
            if user.has_group('vcls-suppliers.vcls_group_rm'):
                rec.access_level = 'rm'
                continue