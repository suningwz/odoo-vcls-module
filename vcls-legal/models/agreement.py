from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "agreement"

    contract_url = fields.Char(String="Contract URL")

    parent_agreement_type = fields.Many2one(related='parent_id.agreement_type_id', required=True)

    parent_agreement_name = fields.Char(related='parent_id.code', required=True)
    # 2 related fields from parent agreement