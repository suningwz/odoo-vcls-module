# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

import logging
import datetime
import math
_logger = logging.getLogger(__name__)


class AnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    stage_id = fields.Selection([
        # ('forecast', 'Stock'),
        ('draft', 'Draft'), 
        ('lc_review', 'LC review'), 
        ('pc_review', 'PC review'), 
        ('carry_forward', 'Carry Forward'),
        ('adjustment_validation', 'Adjustment Validation'),
        ('invoiceable', 'Invoiceable'),
        ('invoiced', 'Invoiced'),
        ('outofscope', 'Out Of Scope'),
        ], default='draft')

    lc_comment = fields.Text(string="Comment")

    deliverable_id = fields.Many2one(
        'product.deliverable',
        string='Deliverable',
        related='product_id.deliverable_id',
        store=True,
    )

    # Used in order to group by client
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='project_id.partner_id',
        store=True,
    )

    adjustment_reason_id = fields.Many2one('timesheet.adjustment.reason', string="Adjustment Reason")

    time_category_id = fields.Many2one(
        comodel_name='project.time_category',
        string="Time Category",
    )

    # Rename description label
    name = fields.Char('External Comment', required=True)

    internal_comment = fields.Char(string='Internal Comment')

    at_risk = fields.Boolean(string='Timesheet at risk', readonly=True)

    # OVERWRITE IN ORDER TO UPDATE LABEL
    unit_amount_rounded = fields.Float(
        string="Revised Time",
        default=0.0,
        copy=False,
    )
    
    required_lc_comment = fields.Boolean(compute='get_required_lc_comment')

    so_line_unit_price = fields.Monetary(
        'Sales Oder Line Unit Price',
        readonly = True,
        #related='so_line.price_unit',
        store=True
    )

    so_line_currency_id = fields.Many2one(
        'res.currency',
        related='so_line.currency_id',
        store=True,
        string='Sales Order Currency',
    )
    adj_reason_required = fields.Boolean()

    connected_employee_seniority_level_id = fields.Many2one(
        comodel_name='hr.employee.seniority.level',
        compute='_get_connected_employee_seniority_level_id',
        string='Default Seniority'
    )

    @api.multi
    def _get_connected_employee_seniority_level_id(self):
        user_id = self.env.user.id
        connected_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
        seniority_level_id = connected_employee_id.seniority_level_id
        for line in self:
            line.connected_employee_seniority_level_id = seniority_level_id

    @api.model
    def _get_at_risk_values(self, project_id, employee_id):
        project = self.env['project.project'].browse(project_id)
        if project.sale_order_id.state not in ['sale', 'done']:
            return True
        employee_id = self.env['hr.employee'].browse(employee_id)

        core_team = project.core_team_id
        if employee_id and core_team:
            project_employee = core_team.consultant_ids | \
                           core_team.ta_ids | \
                           core_team.lead_backup | \
                           core_team.lead_consultant
            if employee_id[0] not in project_employee:
                return True
        return False

    @api.model
    def create(self, vals):
        _logger.info("Create {}".format(vals.get('unit_amount')))

        #when we create a timesheet, we capture the unit price of the so_line_product
        if vals.get('is_timesheet', False) and vals.get('so_line', False) and vals.get('task_id', False):
            task = self.env['project.task'].browse(vals['task_id'])
            so_line = self.env['sale.order.line'].browse(vals['so_line'])
            _logger.info("task line {} so line {}".format(task.sale_line_id,so_line))
            
            if task.sale_line_id != so_line: #if we map to a rate based product
                vals['so_line_unit_price'] = task.sale_line_id.price_unit

        if 'unit_amount' in vals and vals.get('is_timesheet', False):  # do time ceiling for timesheets only
            _logger.info("Before round {}".format(vals.get('unit_amount')))
            if vals['unit_amount'] % 0.25 != 0:
                vals['unit_amount'] = math.ceil(vals.get('unit_amount', 0)*4)/4
                _logger.info("After round {}".format(vals.get('unit_amount')))
        if vals.get('project_id', False):
            vals['at_risk'] = self._get_at_risk_values(vals.get('project_id'),vals.get('employee_id'))
        return super(AnalyticLine, self).create(vals)

    @api.multi
    def write(self, vals):
        # we automatically update the stage if the ts is validated and stage = draft
        so_update = False
        orders = self.env['sale.order']
        #user = self.env['res.users'].browse(self._uid)

        # we manage specific timesheet cases
        if self.is_timesheet and self.project_id:
            # we loop the lines
            for line in self:

                # automatically set the stage to lc_review according to the conditions
                if vals.get('validated',line.validated):
                    if vals.get('stage_id',line.stage_id) == 'draft':
                        vals['stage_id'] = 'lc_review'

                # review of the lc needs sudo() to write on validated ts
                if line.stage_id == 'lc_review':
                    project = self.env['project.project'].browse(vals.get('project_id',line.project_id.id))
                    if project.user_id.id == self._uid: #if the user is the lead consultant, we autorize the modification
                        self.sudo()
                        
                #_logger.info("Test Stage vals {} origin {}".format(vals.get('stage_id','no'),line.stage_id))
                # if one of the 3 important value has changed, and the stage changes the delivered amount
                if (vals.get('date',False) or vals.get('unit_amount_rounded',False) or vals.get('stage_id',False)) and (vals.get('stage_id','no') in ['invoiced','invoiceable'] or line.stage_id in ['invoiced','invoiceable']):
                    _logger.info("Order timesheet update for {}".format(line.name))
                    so_update = True
                    orders |= line.so_line.order_id


        ok = super(AnalyticLine, self).write(vals)
        if ok and so_update:
            orders._compute_timesheet_ids()

        return ok

    @api.multi
    def finalize_lc_review(self):
        self._finalize_lc_review()

    @api.multi
    def _finalize_lc_review(self):
        context = self.env.context
        timesheet_ids = context.get('active_ids',[])
        timesheets = self.env['account.analytic.line'].browse(timesheet_ids)
        if len(timesheets) == 0:
            raise ValidationError(_("Please select at least one record!"))

        timesheets_in = timesheets.filtered(lambda r: r.stage_id=='lc_review' and (r.project_id.user_id.id == r.env.user.id or r.env.user.has_group('vcls-hr.vcls_group_superuser_lvl2')))
        timesheets_out = (timesheets - timesheets_in) if timesheets_in else timesheets
        #_logger.info("names {} stage {} user {} out {}".format(timesheets.mapped('name'),timesheets.mapped('stage_id'),timesheets_out.mapped('name')))
        for timesheet in timesheets_in:
                timesheet.sudo().write({'stage_id':'pc_review'})
        if len(timesheets_out) > 0:
            message = "You don't have the permission for the following timesheet(s) :\n"
            for timesheet in timesheets_out:
                message += " - " + timesheet.name + "\n"
            raise ValidationError(_(message))

    @api.multi
    def finalize_pc_review(self):
        self._finalize_pc_review()

    @api.multi
    def _finalize_pc_review(self):
        if self.env.user.has_group('vcls-hr.vcls_group_superuser_lvl2') or self.env.user.has_group(
                'vcls-hr.vcls_group_controlling'):
            timesheets = self.env['account.analytic.line'].browse(self.env.context.get('active_ids', []))
            adj_validation_timesheets = timesheets.filtered(lambda r: r.unit_amount_rounded != r.unit_amount)
            invoiceable_timesheets = (
                        timesheets - adj_validation_timesheets) if adj_validation_timesheets else timesheets
            adj_validation_timesheets.write({'stage_id': 'adjustment_validation'})
            invoiceable_timesheets.write({'stage_id': 'invoiceable'})
        else:
            raise ValidationError(_("You don't have the permission to finalize pc reviews "))

    @api.multi
    def set_outofscope(self):
        if self.env.user.has_group('vcls-hr.vcls_group_superuser_lvl2') or self.env.user.has_group(
                'vcls-hr.vcls_group_controlling'):
            self.env['account.analytic.line'].browse(self.env.context.get('active_ids', [])).write({'stage_id': 'outofscope'})
        else:
            raise ValidationError(_("You don't have the permission to set timesheets to Out of Scope stage."))

    @api.multi
    def set_carry_forward(self):
        if self.env.user.has_group('vcls-hr.vcls_group_superuser_lvl2') or self.env.user.has_group(
                'vcls-hr.vcls_group_controlling'):
            self.env['account.analytic.line'].browse(self._context.get('active_ids', False)).write(
                {'stage_id': 'carry_forward'})
        else:
            raise ValidationError(_("You don't have the permission to set timesheets to Carry Forward stage."))

    @api.depends('user_id')
    def _compute_employee_id(self):
        for record in self:
            if record.user_id:
                resource = self.env['resource.resource'].search([('user_id','=',record.user_id.id)])
                employee = self.env['hr.employee'].search([('resource_id','=',resource.id)])
                record.employee_id = employee
    
    
    """@api.depends('user_id')
    def _is_authorized_lm(self):
        for record in self:
            try:
                resource = self.env['resource.resource'].search([('user_id','=',record.user_id.id)])
                employee = self.env['hr.employee'].search([('resource_id','=',resource.id)])
                record.is_authorized = self._uid == employee.parent_id.id
            except Exception as err:
                print(err)
                # No project / project controller / project manager
                record.is_authorized = False"""
    

    @api.onchange('unit_amount_rounded', 'unit_amount')
    def get_required_lc_comment(self):
        for record in self:
            if float_compare(record.unit_amount_rounded, record.unit_amount, precision_digits=2) == 0:
                record.required_lc_comment = False
            else:
                record.required_lc_comment = True    

    @api.onchange('project_id')
    def onchange_project_id(self):
        # force domain on task when project is set
        if self.project_id:
            if self.project_id != self.task_id.project_id:
                # reset task when changing project
                self.task_id = False
            return {'domain': {
                'task_id': [('project_id', '=', self.project_id.id), ('stage_id.allow_timesheet','=', True)]
            }}

    @api.onchange('unit_amount_rounded')
    def onchange_adj_reason_readonly(self):
        adj_reason_required = False
        if self.unit_amount != self.unit_amount_rounded:
            adj_reason_required = True
        self.adj_reason_required = adj_reason_required

    @api.multi
    def button_details_lc(self):
        view = {
            'name': _('Details'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.analytic.line',
            'view_id': self.env.ref('vcls-timesheet.vcls_timesheet_lc_view_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
            'form_view_initial_mode': 'edit',
            'force_detailed_view': True,
            'set_fields_readonly': self.stage_id != 'lc_review'},
            'res_id': self.id,
        }
        return view
    
    @api.multi
    def button_details_pc(self):
        view = {
            'name': _('Details'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.analytic.line',
            'view_id': self.env.ref('vcls-timesheet.vcls_timesheet_pc_view_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
            'form_view_initial_mode': 'edit',
            'force_detailed_view': True, },
            'res_id': self.id,
        }
        return view

    def lc_review_approve_timesheets(self):
        self.search([('stage_id', '=', 'lc_review')]).write({'stage_id': 'pc_review'})

    def pc_review_approve_timesheets(self):
        self.search([('stage_id', '=', 'pc_review'), ('lc_comment', '=', False)]).\
            write({'stage_id': 'invoiceable'})
