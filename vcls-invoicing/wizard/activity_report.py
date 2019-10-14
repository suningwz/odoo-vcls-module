from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ActivityReportGroupment(models.TransientModel):
    _name = 'activity.report.groupment'
    
    def get_activity_report_template(self):
        if self._context.get('invoice_id'):
            invoice_id = self.env['account.invoice'].browse(self._context['invoice_id'])
            return invoice_id.invoice_line_ids.mapped("sale_line_ids.order_id").activity_report_template.id
        return False
    
    invoice_id = fields.Many2one('account.invoice', readonly=True,
                                 default=lambda self: self._context.get('default_invoice_id', False))
    groupment_by = fields.Selection([('project', 'Project'), ('task', 'Task'),
                                    ('deliverable', 'Deliverable'), ('time_category', 'Time category'),
                                    ('product_name', 'Products name'), ('external_comment', "Name")],
                                    string='Group by', required=True)
    activity_report_template = fields.Many2one('ir.actions.report',
                                               default=lambda self: self.get_activity_report_template(), readonly=True)

    @api.multi
    def get_grouping(self):
        self.ensure_one()
        if not self.invoice_id.timesheet_ids:
            return []
        domain = [('id', 'in', self.invoice_id.timesheet_ids.ids)]
        analytic_acc = self.env['account.analytic.line']
        result = []
        if self.groupment_by == 'project':
            timesheets_ids = analytic_acc.read_group(
                domain=domain,
                fields=['unit_amount_rounded'],
                groupby=['project_id'])
            for dom_line in timesheets_ids:
                if dom_line.get('project_id'):
                    result.append({'name': dom_line['project_id'][1],
                                   'qty': dom_line.get('unit_amount_rounded', 0)})
        elif self.groupment_by == 'task':
            timesheets_ids = analytic_acc.read_group(
                domain=domain,
                fields=['unit_amount_rounded'],
                groupby=['task_id'])
            for dom_line in timesheets_ids:
                if dom_line.get('task_id'):
                    result.append({'name': dom_line['task_id'][1],
                                   'qty': dom_line.get('unit_amount_rounded', 0)})
        elif self.groupment_by == 'deliverable':
            timesheets_ids = analytic_acc.read_group(
                domain=domain,
                fields=['unit_amount_rounded'],
                groupby=['deliverable_id'])
            for dom_line in timesheets_ids:
                if dom_line.get('deliverable_id'):
                    result.append({'name': dom_line['deliverable_id'][1],
                                   'qty': dom_line.get('unit_amount_rounded', 0)})
        elif self.groupment_by == 'time_category':
            timesheets_ids = analytic_acc.read_group(
                domain=domain,
                fields=['unit_amount_rounded'],
                groupby=['time_category_id'])
            for dom_line in timesheets_ids:
                if dom_line.get('time_category_id'):
                    result.append({'name': dom_line['time_category_id'][1],
                                   'qty': dom_line.get('unit_amount_rounded', 0)})
        elif self.groupment_by == 'product_name':
            timesheets_ids = analytic_acc.read_group(
                domain=domain,
                fields=['unit_amount_rounded'],
                groupby=['product_name'])
            for dom_line in timesheets_ids:
                if dom_line.get('product_name'):
                    result.append({'name': dom_line['product_name'][1],
                                   'qty': dom_line.get('unit_amount_rounded', 0)})
        elif self.groupment_by == 'external_comment':
            timesheets_ids = analytic_acc.read_group(
                domain=domain,
                fields=['unit_amount_rounded'],
                groupby=['external_comment'])
            for dom_line in timesheets_ids:
                if dom_line.get('external_comment'):
                    result.append({'name': dom_line['external_comment'][1],
                                   'qty': dom_line.get('unit_amount_rounded', 0)})
        return result

    def action_get_report(self):
        return self.env.ref('vcls-invoicing.invoice_activity_report').report_action(self, config=False)

    @api.onchange('groupment_by')
    def onchange_groupment_by(self):
        if not self.activity_report_template and self.groupment_by == 'external_comment':
            raise ValidationError('Please select a Groupment different from Name')
