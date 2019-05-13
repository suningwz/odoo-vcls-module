# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PartnerRelations(models.Model):

    _name = 'res.partner.relation'
    _description = 'Used to map a set of predefined relation types between partners.'

    """relation_type = fields.Selection([
        ('company_parent', 'Parent Company'),
        ('company_acquisition', 'Aquired Company'),
        ('individual_transfer', 'Individual Transfer'),
        ],
    )"""
    
    source_partner_id = fields.Many2one(
        'res.partner',
        string = 'Source Partner',
        required = True,
    )

    target_partner_id = fields.Many2one(
        'res.partner',
        string = 'Target Partner',
        required = True,
    )