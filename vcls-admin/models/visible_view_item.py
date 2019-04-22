# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class VisibleViewItem(models.Model):

    _name = 'visible.view.item'

    view_ref = fields.Char()
    item_name = fields.Char()