from odoo import api, models


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    @api.model
    def default_get(self, fields):
        """
        Override of default_get to get the context default_attachment_ids
        """
        res = super(AccountInvoiceSend, self).default_get(fields)
        if 'composer_id' in res and self._context.get('default_attachment_ids'):
            composer = self.env['mail.compose.message'].browse(res['composer_id'])
            composer.attachment_ids = self._context.get('default_attachment_ids')
        return res

    @api.onchange('template_id')
    def onchange_template_id(self):
        super(AccountInvoiceSend, self).onchange_template_id()
        self.attachment_ids = self.env['ir.attachment'].browse(self._context.get('default_attachment_ids', []))
