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

    expertise_id = fields.Many2many(
        'expertise.area',
        string="Area of Expertise",
    )

    deliverable_ids = fields.Many2many(
        'product.deliverable',
    )

    access_level = fields.Selection([
        ('rm', 'Resource Manager'),
        ('lc', 'Lead Consultant'),], 
        compute='_get_access_level',
        store=False,
        default='lc',)

    supplier_stage = fields.Selection(
        related='partner_id.stage',
        readonly=True,
    )

    scope_of_work = fields.Html(
        string="Scope of Work"
    )

    default_rate_id = fields.Many2one(
        comodel_name = 'product.template',
        domain = "[('vcls_type','=','rate')]",
        compute = '_compute_default_rate_id',
        store = True,
    )

    ###################
    # COMPUTE METHODS #
    ###################
    @api.depends('partner_id')
    def _compute_default_rate_id(self):
        for purchase in self:
            #we search for an employee, having a user linked to the partner_id
            ext_employee = self.env['hr.employee'].search([('user_id.partner_id','=',purchase.partner_id.id)],limit=1)
            if ext_employee.default_rate_ids:
                purchase.default_rate_id = ext_employee.default_rate_ids[0]

    @api.multi
    def _get_access_level(self):
        user = self.env['res.users'].browse(self._uid)

        for rec in self:           
            #if rm
            if user.has_group('vcls-suppliers.vcls_group_rm'):
                rec.access_level = 'rm'
                continue
    
    