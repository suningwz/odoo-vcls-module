# See LICENSE file for full copyright and licensing details.
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super(ResUsers, self).__init__(pool, cr)

        type(self).SELF_WRITEABLE_FIELDS = list(set(self.SELF_WRITEABLE_FIELDS + ['contact_sync_use_category', 'contact_sync_filter_options', 'contact_sync_filters']))

        return init_res
