from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ActivityReportWizard(models.TransientModel):
    _name = 'activity.report.wizard'
    _description = 'activity.report.wizard'

    def get_activity_report_template(self):
        if self._context.get('invoice_id'):
            invoice_id = self.env['account.invoice'].browse(self._context['invoice_id'])
            return invoice_id.invoice_line_ids.mapped("sale_line_ids.order_id").activity_report_template.id
        return False
    
    invoice_id = fields.Many2one('account.invoice', readonly=True,
                                 default=lambda self: self._context.get('default_invoice_id', False))

    activity_report_template = fields.Many2one('ir.actions.report',
                                               default=lambda self: self.get_activity_report_template(), readonly=True)

    report_type = fields.Selection([
        ('simple', 'Simple'),
        ('detailed', 'Detailed'),
    ], default='simple')

    def action_get_report(self):
        report_ref = None
        if self.report_type == 'simple':
            report_ref = 'vcls-invoicing.invoice_activity_simple_report'
        elif self.report_type == 'detailed':
            report_ref = 'vcls-invoicing.invoice_activity_detailed_report'
        if report_ref:
            return self.env.ref(report_ref).report_action(
                self.invoice_id, config=False
            )

    @api.onchange('groupment_by')
    def onchange_groupment_by(self):
        if not self.activity_report_template and self.groupment_by == 'external_comment':
            raise ValidationError('Please select a Groupment different from Name')
