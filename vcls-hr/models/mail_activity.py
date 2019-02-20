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
    _inherit = 'mail.activity.type'
    
    
    ''' We override the below method in order to have a specific body template for the leave approval case'''
    @api.multi
    def action_notify(self):
        body_template = self.env.ref('mail.message_activity_assigned')
        for activity in self:
            # if this is a leave approval activity_type
            raise ValidationError('{} = {}'.format(activity.activity_type_id.id,self.env.ref('hr_holidays.mail_act_leave_approval').id))
            if activity.activity_type_id.id == self.env.ref('hr_holidays.mail_act_leave_approval').id:
                body_template = self.env.ref('vcls-hr.message_activity_leave')
                
            
            model_description = self.env['ir.model']._get(activity.res_model).display_name
            body = body_template.render(
                dict(activity=activity, model_description=model_description),
                engine='ir.qweb',
                minimal_qcontext=True
            )
            self.env['mail.thread'].message_notify(
                partner_ids=activity.user_id.partner_id.ids,
                body=body,
                subject=_('%s: %s assigned to you') % (activity.res_name, activity.summary or activity.activity_type_id.name),
                record_name=activity.res_name,
                model_description=model_description,
                notif_layout='mail.mail_notification_light'
            )