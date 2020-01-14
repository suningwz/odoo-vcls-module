# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _


class TaskMarketing(models.Model):
    _name = 'task.marketing'
    _inherit = 'project.task'
    _description = 'Task marketing'

    organizer_id = fields.Many2one(
        'res.partner',
        string='Organizer'
    )
    business_line_id = fields.Many2one(
        'product.category',
        string='Business line',
        domain='[("is_business_line", "=", True)]'
    )
    country_group_id = fields.Many2one(
        'res.country.group',
        string='Country group',
    )

