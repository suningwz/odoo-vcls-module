# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PartnerRelations(models.Model):

    _name = 'res.partner.relation'
    _description = 'Map partners relations'
    
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

    source_message = fields.Char(
        related = 'type_id.source_message',
    )

    target_message = fields.Char(
        related = 'type_id.target_message',
    )

    # related + depends
    '''
    source_category = fields.Many2many('res.partner.category', column1='partner_id',
                                    column2='category_id', string='Source Tags', related='source_partner_id.category_id')


    def update_child_tags(self):
        # scheduled actions
        group_relations = self.env['res.partner.relation'].search([('type_id', '=', self.env.ref('vcls-crm.rel_type_cmpny_group').id)])
        for relation in group_relations:
            relation.target_partner_id.category_id = [(6, 0, relation.source_partner_id.category_id.ids)]
    '''

class PartnerRelationType(models.Model):

    _name = 'partner.relation.type'
    _description = 'Predefined relations between partners.'

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