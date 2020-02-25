# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class LeadQuotation(models.TransientModel):
    _name = 'lead.quotation.wizard'
    _description = 'Lead Quotation Wizard'

    quotation_type = fields.Selection([
        ('new', 'New project'),
        ('budget_extension', 'Budget extension'),
        ('scope_extension', 'Scope extension'),
    ], string='Quotation type', required=True, default='new'
    )
    existing_quotation_id = fields.Many2one(
        'sale.order', string="Existing quotation"
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        action = self.env.ref('sale_crm.sale_action_quotations_new').read()[0]
        _logger.info("OPP to QUOTE before: {}".format(action['context']))
        context = self._context
        active_model = context.get('active_model', '')
        active_id = context.get('active_id')
        _logger.info("OPP to QUOTE context {}".format(context))
        if not active_model == 'crm.lead' or not active_id:
            return
        lead = self.env['crm.lead'].browse(active_id)
        additional_context = {
            'search_default_partner_id': lead.partner_id.parent_id.id or lead.partner_id.id,
            'default_partner_id': lead.partner_id.parent_id.id or lead.partner_id.id,
            'default_partner_shipping_id': lead.partner_id.id,
            'default_team_id': lead.team_id.id,
            'default_campaign_id': lead.campaign_id.id,
            'default_medium_id': lead.medium_id.id,
            'default_origin': lead.name,
            'default_source_id': lead.source_id.id,
            'default_opportunity_id': lead.id,
            'default_program_id': lead.program_id.id,
            'default_scope_of_work': lead.scope_of_work,
            'default_product_category_id': lead.product_category_id.id,
            'default_expected_start_date': lead.expected_start_date,
            'lead_quotation_type': self.quotation_type,
        }

        action['context'] = additional_context
        if self.quotation_type == 'new':
            return action
        if self.quotation_type in ('budget_extension', 'scope_extension') and self.existing_quotation_id:
            # copy the quotation content
            fields_to_copy = [
                'pricelist_id', 'currency_id', 'note', 'team_id',
                'tag_ids', 'active', 'fiscal_position_id', 'risk_score', 'program_id',
                'company_id', 'deliverable_id', 'product_category_id', 'business_mode',
                'agreement_id', 'po_id', 'payment_term_id', 'validity_date',
                'scope_of_work', 'user_id', 'core_team_id', 'invoicing_frequency',
                'risk_ids', 'expected_start_date', 'expected_end_date',
            ]
            values = self.existing_quotation_id.read(fields_to_copy)[0]
            all_quotation_fields = self.existing_quotation_id._fields
            default_values = dict(
                ('default_{}'
                 .format(k),
                 v and v[0] or False if all_quotation_fields[k].type == 'many2one' else v)
                for k, v in values.items()
            )
            action['context'].update(default_values)

            # copy order lines
            if self.quotation_type == 'budget_extension':
                order_lines_values = self.existing_quotation_id.order_line.read()
                all_order_line_fields = self.existing_quotation_id.order_line._fields
                no_copy_lines_fields = ('project_id', 'task_id', 'analytic_line_ids')
                for order_line_values in order_lines_values:
                    for field_name, value in order_line_values.items():
                        if field_name in no_copy_lines_fields:
                            order_line_values[field_name] = False
                            continue
                        if all_order_line_fields[field_name].type == 'many2one':
                            order_line_values[field_name] = value and value[0] or False
                        elif field_name == 'price_unit' and order_line_values[field_name] == 'vcls_service':
                            all_order_line_fields[field_name] = 0
                order_lines = [(5, 0, 0)] + [
                    (0, 0, values)
                    for values in order_lines_values
                ]
                action['context'].update({
                    'default_order_line': order_lines,
                })
            # copy parent_id
            action['context'].update({
                'default_parent_sale_order_id': self.existing_quotation_id.id,
            })
        return action
