# See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime, date

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AzureADChangeQueuer(models.AbstractModel):
    _inherit = 'azure.ad.change.queuer'
   
    @api.multi
    def _get_observed_changed_values_simple_types(self, values):

        if not self.env.user.context_data_integration:
            return super(AzureADChangeQueuer, self)._get_observed_changed_values_simple_types(values)
        
        else:
            return {}

