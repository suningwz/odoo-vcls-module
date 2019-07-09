from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    contract_url = fields.Char(String="Contract URL")

    # 2 related fields from parent agreement

    parent_agreement_type = fields.Many2one(
        related='parent_agreement_id.agreement_type_id',
        #required=True, 
        string='Parent Type',
        )

    parent_agreement_name = fields.Char(
        related='parent_agreement_id.name', 
        #required=True,
        string = 'Parent Name',
        )
    

    internal_name = fields.Char(String="Internal Name")