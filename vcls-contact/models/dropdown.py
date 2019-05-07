# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ClientActivity(models.Model):

    _name = 'client.activity'

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )

class ClientProduct(models.Model):

    _name = 'client.product'

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )

class FunctionalFocus(models.Model):

    _name = 'partner.functional.focus'

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )

class PartnerSeniority(models.Model):

    _name = 'partner.seniority'

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )