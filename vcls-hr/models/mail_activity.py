# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
import pytz

from odoo import api, exceptions, fields, models, _

from odoo.tools import pycompat
from odoo.tools.misc import clean_context

_logger = logging.getLogger(__name__)


class MailActivityType(models.Model):
    """ Overrides the initial class """
    _inherit = 'mail.activity'
    
    
    ''' We override the below method in order to have a specific body template for the leave approval case'''
    @api.multi
    def action_notify(self):
        body_template = self.env.ref('mail.message_activity_assigned')
        for activity in self:
            subject=_('%s: %s assigned to you') % (activity.res_name, activity.summary or activity.activity_type_id.name),
            # if this is a leave approval activity_type
            if activity.activity_type_id.id == self.env.ref('hr_holidays.mail_act_leave_approval').id:
                body_template = self.env.ref('vcls-hr.message_activity_leave')
                subject=_('Kalpa | Leave Request from {}'.format(activity.create_user_id.name)) 
                
                
            model_description = self.env['ir.model']._get(activity.res_model).display_name
            body = body_template.render(
                dict(activity=activity, model_description=model_description),
                engine='ir.qweb',
                minimal_qcontext=True
            )
            
            self.env['mail.thread'].message_notify(
                partner_ids=activity.user_id.partner_id.ids,
                body=body,
                subject=subject,
                record_name=activity.res_name,
                model_description=model_description,
                notif_layout='mail.mail_notification_light'
            )