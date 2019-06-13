# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

class ProjectProgram(models.Model):

    _name = 'project.program'
    _description = 'A Program of Projects'

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

### ADD PROGRAM TO OTHER MODELS ###
class Client(models.Model):

    _inherit = 'res.partner'

    program_ids = fields.One2many(
        'project.program',
        'client_id',
        string = 'Client Programs',
        readonly = True,
    )

    program_count = fields.Integer(
        compute = '_compute_program_count',
    )

    ### METHODS ###
    @api.depends('program_ids')
    def _compute_program_count(self):
        for client in self:
            client.program_count = len(client.program_ids)

class Lead(models.Model):

    _inherit = 'crm.lead'

    program_id = fields.Many2one(
        comodel_name = 'project.program',
        string = 'Related Program',
    )



class SaleOrder(models.Model):

    _inherit = 'sale.order'

    program_id = fields.Many2one(
        comodel_name = 'project.program',
        string = 'Related Program',
    )    

class Project(models.Model):

    _inherit = 'project.project'

    program_id = fields.Many2one(
        comodel_name = 'project.program',
        string = 'Related Program',
    )