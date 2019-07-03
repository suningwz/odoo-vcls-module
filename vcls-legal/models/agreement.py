from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    contract_url = fields.Char(String="Contract URL")

    parent_agreement_type = fields.Many2one(related='parent_agreement_id.agreement_type_id', required=True)

    parent_agreement_name = fields.Char(related='parent_agreement_id.code', required=True)
    # 2 related fields from parent agreement

    internal_name = fields.Char(String="Internal Name")