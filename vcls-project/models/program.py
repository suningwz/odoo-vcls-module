# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class ProjectProgram(models.Model):

    _inherit = 'project.program'

    name = fields.Char()

    active = fields.Boolean(
        default = True,
    )

    client_id = fields.Many2one(
        comodel_name = 'res.partner',
        domain = "[('customer','=',True)]",
        string = 'Related Client',
        required = True,
    )

    leader_id = fields.Many2one(
        comodel_name = 'res.users',
        string = 'Program Leader',
    )

    product_name = fields.Char(
        string = "Product Name",
        help = 'The client product name',
    )

    indication = fields.Char()