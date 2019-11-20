
# -*- coding: utf-8 -*-

from odoo import models, api


class PatchFieldView(models.AbstractModel):
    _name = 'patch.field.view'
    _description = 'Patch fields view'

    @api.model_cr
    def _register_hook(self):
        """ Patch all models to make fields_get replace 'Salesperson' with
            'Account Manager' if the actual language is english.
        """

        def make_fields_get():

            @api.model
            def do_fields_get(self, allfields=None, attributes=None):
                res = do_fields_get.origin(self, allfields, attributes)
                lang = self._context.get('lang', '')
                lang = isinstance(lang, str) and lang[:2] or 'en'
                for field_name, result in res.items():
                    if 'salesperson' in result.get('string', '').lower() and lang == 'en':
                        string = result['string']
                        result['string'] = string.replace('Salesperson', 'Account Manager') \
                            .replace('salesperson', 'account manager')
                return res
            return do_fields_get

        for key, model in self.env.items():
            model._patch_method('fields_get', make_fields_get())
