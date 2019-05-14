# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PartnerRelations(models.Model):

    _name = 'res.partner.relation'
    _description = 'Used to map a set of predefined relation types between partners.'
    
    type_id = fields.Many2one(
        'partner.relation.type',
        string = "Relation Type",
        required = True,
    )
    
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

class PartnerRelationType(models.Model):

    _name = 'partner.relation.type'
    _description = 'Predefined relations between partners.'

    """relation_type = fields.Selection([
        ('company_parent', 'Parent Company'),
        ('company_acquisition', 'Aquired Company'),
        ('individual_transfer', 'Individual Transfer'),
        ],
    )"""

    name = fields.Char(
        required = True,
    )
    active = fields.Boolean(
        default = True,
    )

    description = fields.Char()

    source_message = fields.Char()
    source_domain  = fields.Char()

    target_message = fields.Char()
    target_domain  = fields.Char()