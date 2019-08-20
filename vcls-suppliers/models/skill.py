# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class UserSkill(models.Model):

    _name = 'res.partner.skill'
    _description = 'Product as user skill'
    _sql_constraints = [
        (
            'user_skill_uniq',
            'unique(user_id, skill_id)',
            'This resource already has that skill!'
        ),
    ]

    user_id = fields.Many2one(
        string='Resource Contact',
        comodel_name='res.partner',
        domain="[('company_type','=','person')]",
    )

    skill_id = fields.Many2one(
        string='Skill',
        comodel_name='product.template',
        domain="[('is_skill','=',True)]",
    )

    level = fields.Selection(
        string='Level',
        selection=[
            ('0', 'Junior'),
            ('1', 'Intermediate'),
            ('2', 'Senior'),
            ('3', 'Expert'),
        ],
    )

    time_spent = fields.Float(
        default = 0.0,
        readonly=True,
    )


    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
    )

    comment = fields.Char()

    
    @api.multi
    @api.depends('user_id.name', 'skill_id.name', 'level')
    def _compute_complete_name(self):
        levels = dict(self._fields['level'].selection)
        for skill in self:
            skill.complete_name = _(
                '%(user)s, %(skill)s (%(level)s)'
            ) % {
                'user': skill.user_id.name,
                'skill': skill.skill_id.name,
                'level': levels.get(skill.level),
            }