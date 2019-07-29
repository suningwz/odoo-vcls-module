# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _
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
        ('adjustment_validation', 'Adjustment Validation'),
        ('invoiceable', 'Invoiceable'),
        ('outofscope', 'Out Of Scope'),
        ], default='draft')

    lc_comment = fields.Text(string = "Comment")

    deliverable_id = fields.Many2one(
        'product.deliverable',
        string = 'Deliverable',
        related = 'product_id.deliverable_id',
        store = True,
    )

    # Used in order to group by client
    partner_id = fields.Many2one(
        'res.partner',
        string = 'Client',
        related = 'project_id.partner_id',
        store = True,
    )

    project_user_id = fields.Many2one(
        'res.users',
        string = 'Project Controller',
        related = 'project_id.user_id',
        store = True,
    )

    adjustment_reason_id = fields.Many2one('timesheet.adjustment.reason', string="Adjustment Reason")

    # Rename description label
    name = fields.Char('External Comment', required=True)

    internal_comment = fields.Char(string = 'Internal Comment')

    is_authorized = fields.Boolean(
        'LM can see',
        compute = '_is_authorized_lm',
        store = True
    )


    @api.model
    def create(self, vals):
        if 'unit_amount' in vals and vals.get('is_timesheet',False): #do time ceiling for timesheets only
            if vals['unit_amount'] % 0.25 != 0:
                vals['unit_amount'] = math.ceil(vals['unit_amount']*4)/4
        return super(AnalyticLine, self).create(vals)

    @api.multi
    def _finalize_lc_review(self):
        context = self.env.context
        timesheet_ids = context.get('active_ids',[])
        timesheets = self.env['account.analytic.line'].browse(timesheet_ids)
        if len(timesheets) == 0:
            raise ValidationError(_("Please select at least one record!"))

        timesheets_in = timesheets.filtered(lambda r: (r.stage_id=='draft' and (r.project_id.user_id.id == r.env.user.id or r.env.user.has_group('vcls-hr.vcls_group_superuser_lvl2'))))
        timesheets_out = timesheets - timesheets_in
        #timesheets_out = timesheets.filtered(lambda r: (r.stage_id=='draft' and r.project_id.user_id.id != r.env.user.id and not r.env.user.has_group('vcls-hr.vcls_group_superuser_lvl2')))
        for timesheet in timesheets_in:
                timesheet.write({'stage_id':'pc_review'})
        if len(timesheets_out) > 0:
            message = "You don't have the permission for the following timesheet(s) :\n"
            for timesheet in timesheets_out:
                message += " - " + timesheet.name + "\n"
            raise ValidationError(_(message))

    
    @api.multi
    def _finalize_pc_review(self):
        context = self.env.context
        timesheet_ids = context.get('active_ids',[])
        timesheets = self.env['account.analytic.line'].browse(timesheet_ids)
        if len(timesheets) == 0:
            raise ValidationError(_("Please select at least one record!"))
        timesheets_in = timesheets.filtered(lambda r: (r.env.user.has_group('vcls-hr.vcls_group_superuser_lvl2') or r.env.user.has_group('vcls-timesheet.vcls_pc'))).write({'stage_id':'invoiceable'})
        timesheets_out = timesheets - timesheets_in
        for timesheet in timesheets_in:
            if timesheet.unit_amount_rounded != timesheet.unit_amount:
                timesheet.write({'stage_id':'adjustment_validation'})
            else:
                timesheet.write({'stage_id':'invoiceable'})
        if len(timesheets_out) > 0:
            message = "You don't have the permission for the following timesheet(s) :\n"
            for timesheet in timesheets_out:
                message += "- " + timesheet.name + "\n"
            raise ValidationError(_(message))
    
    @api.multi
    def set_outofscope(self):
        context = self.env.context
        timesheet_ids = context.get('active_ids',[])
        timesheets = self.env['account.analytic.line'].browse(timesheet_ids)
        timesheets.filtered(lambda r: (r.task_id.project_id.user_id.id == self._uid or r.env.user.has_group('vcls-timesheet.vcls_pc'))).write({'stage_id':'outofscope'})
    
    @api.depends('user_id')
    def _compute_employee_id(self):
        for record in self:
            if record.user_id:
                resource = self.env['resource.resource'].search([('user_id','=',record.user_id.id)])
                employee = self.env['hr.employee'].search([('resource_id','=',resource.id)])
                record.employee_id = employee
    
    @api.depends('user_id')
    def _is_authorized_lm(self):
        for record in self:
            try:
                resource = self.env['resource.resource'].search([('user_id','=',record.user_id.id)])
                employee = self.env['hr.employee'].search([('resource_id','=',resource.id)])
                record.is_authorized = self._uid in employee.lm_ids.ids
            except Exception as err:
                print(err)
                # No project / project controller / project manager
                record.is_authorized = False


    
