# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import datetime
import traceback

from collections import Counter
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import format_date
from odoo.tools.safe_eval import safe_eval

from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    management_mode = fields.Selection([
        ('std', 'Standard'),
        ('deliver', 'Deliver in Source Order'),], 
        string="Management Mode",
        store=True,
        compute = '_compute_management_mode',
        help="Standard | Use the Odoo way of managing subscriptions.\nDeliver | No invoice is generated, but the quantity is delivered after each period.",
        )

    @api.depends('recurring_invoice_line_ids')
    def _compute_management_mode(self):
        for sub in self:
            product_policies = sub.recurring_invoice_line_ids.mapped('product_id.service_policy')
            if list(set(product_policies)) == ['delivered_manual']: #if all products are in delivered_manual policy
                sub.management_mode='deliver'
            else:
                sub.management_mode='std'
            
            _logger.info("SUB | {} | {} | {}".format(sub.display_name,list(set(product_policies)),sub.management_mode))

    @api.multi
    def _recurring_create_invoice(self, automatic=False):
        #we initiate the list of subscriptions to be processed before to filter according to the management_mode
        current_date = datetime.date.today()

        if len(self) > 0:
            subscriptions = self
        else:
            domain = [('recurring_next_date', '<=', current_date),('recurring_next_date', '>', 'date_start'),
                      '|', ('in_progress', '=', True), ('to_renew', '=', True)]
            subscriptions = self.search(domain)

        std_subs = subscriptions.filtered(lambda s: s.management_mode=='std')
        _logger.info("SUB | {} standard subscriptions to process.".format(len(std_subs)))
        super(SaleSubscription,std_subs)._recurring_create_invoice(automatic)

        deliver_subs = subscriptions.filtered(lambda s: s.management_mode=='deliver')
        _logger.info("SUB | {} deliver subscriptions to process.".format(len(deliver_subs)))

"""    
class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"
    """