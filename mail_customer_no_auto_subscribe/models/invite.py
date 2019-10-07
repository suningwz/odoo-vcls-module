# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    @api.multi
    def add_followers(self):
        return super(Invite, self.with_context(allow_auto_follow=True))\
            .add_followers()
