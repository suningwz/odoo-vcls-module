# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ClientActivity(models.Model):

    _name = 'client.activity'
    _description = "Used to segment clients according to their activity"

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )

class ClientProduct(models.Model):

    _name = 'client.product'
    _description = "Used to segment clients according to their type of product"

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )

class FunctionalFocus(models.Model):

    _name = 'partner.functional.focus'
    _description = "Used to segment individuals according to their function in the company."

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )

class PartnerSeniority(models.Model):

    _name = 'partner.seniority'
    _description = "Used to segment individuals according to their decision level in a company."

    active = fields.Boolean(
        default = True,
    )
    name = fields.Char(
        required = True,
    )