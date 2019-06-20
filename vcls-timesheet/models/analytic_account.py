# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

import logging
import datetime
import math
_logger = logging.getLogger(__name__)

class AnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    stage_id = fields.Selection([
        ('draft', 'Draft'), 
        ('lc_review', 'LC review'), 
        ('pc_review', 'PC review'), 
        ('carry_forward', 'Carry Forward'),
        ('invoiceable', 'Invoiceable') 
        ], default='draft')

    lc_comment = fields.Text(string = "Comment")

    deliverable_id = fields.Many2one(
        'product.deliverable',
        string = 'Deliverable',
        related = 'product_id.deliverable_id',
        store = True,
    )

    @api.model
    def create(self, vals):
        if 'unit_amount' in vals and vals.get('is_timesheet',False): #do time ceiling for timesheets only
            if vals['unit_amount'] % 0.25 != 0:
                vals['unit_amount'] = math.ceil(vals['unit_amount']*4)/4
        return super(AnalyticLine, self).create(vals)

    # Replaced by an approval at the employee level (timesheet_validated field)
    """@api.model
    def approve_timesheets(self):
        last_timesheet_lock = datetime.datetime.now() - datetime.timedelta(days=1)
        timesheets = self.env['account.analytic.line'].search([('validated','=',False)])
        timesheets.write({'validated':True, 'stage_id':'lc_review'})
        #for ts in timesheets:
            #ts.write({'validated':True, 'stage_id':'lc_review'})

        self.env.ref('vcls-timesheet.last_timesheet_lock').value = last_timesheet_lock"""

    @api.multi
    def _finalize_lc_review(self):
        context = self.env.context
        timesheet_ids = context.get('active_ids',[])
        timesheets = self.env['account.analytic.line'].browse(timesheet_ids)
        timesheets.filtered(lambda r: (r.stage_id=='draft',r.lc_comment==True)).write({'stage_id':'pc_review'})
        timesheets.filtered(lambda r: (r.stage_id=='draft',r.lc_comment==False)).write({'stage_id':'invoiceable'})


        """for timesheet_id in timesheet_ids:
            timesheet = self.env['account.analytic.line'].browse(timesheet_id)
            if timesheet.lc_comment != False:
                timesheet.write({'stage_id':'pc_review'})
            else:
                timesheet.write({'stage_id':'invoiceable'})"""
    

    
