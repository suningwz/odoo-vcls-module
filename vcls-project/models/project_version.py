# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectVersion(models.Model):
    _name = 'project.version'

    """ This model will be used to assign a target version to a set of tasks in order to allow agile project management """

    name = fields.Char(
        readonly = True,
        store = True,
        compute = "_compute_name",
    )

    active = fields.Boolean(
        default = True,
    )

    project_id = fields.Many2one(
        'project.project',
        string = 'Related Project',
        required = True,
    )

    version_number = fields.Char(
        string = "Version Number",
        required = True,
    )

    version_name = fields.Char(
        string = "Version Name",
        required = True,
    )

    target_date = fields.Date(
        string = "Target Delivery Date",
    )

    description = fields.Char()

    status = fields.Selection([
        ('prod','In Production'),
        ('stage','In Staging'),
        ('dev','In Development'),
        ('future','Future'),],
        string = "Version Status",
        )

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('version_name','version_number')
    def _compute_name(self):
        for ver in self:
            if ver.version_name and ver.version_number:
                ver.name = "{} | {}".format(ver.version_number,ver.version_name)