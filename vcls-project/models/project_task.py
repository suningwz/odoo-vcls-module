# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    business_value = fields.Selection([
        ('1', 'Minor'),
        ('2', 'Moderate'),
        ('3', 'Strong'),
        ('4', 'Major')],
        string = 'Business Value',
    )

    dev_effort = fields.Selection([
        ('1', 'Small'),
        ('2', 'Medium'),
        ('3', 'Large'),
        ('4', 'Xtra Large')],
        string = 'Effort Assumption',
    )
