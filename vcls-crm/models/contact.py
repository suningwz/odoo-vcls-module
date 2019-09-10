# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions

class ContactExt(models.Model):

    _inherit = 'res.partner'
    
    ###  ###
    relation_ids = fields.Many2many(
        'res.partner.relation',
        readonly = True,
        string = 'Mapped Relations',
    )

    ### MARKETING FIELDS FOR TRACEABILITY ###
    
    #Marketing fields
    opted_in = fields.Boolean(
        string = 'Opted In',
    )

    opted_out = fields.Boolean(
        string = 'Opted Out',
    )

    vcls_contact_id = fields.Many2one(
        'res.users',
        string = "Initial Contact",
        domain = "[('employee','=',True)]",
    )

    default_currency_id = fields.Many2one(
        'res.currency',
        compute='_get_default_currency',
        inverse='_set_default_currency',
    )

    core_process_index = fields.Integer(
        default = 1,
        )

    middlename = fields.Char(
        "Middle name",
        index=True,
    )

    @api.model
    def _get_computed_name(self, lastname, firstname, middlename):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        order = self._get_names_order()
        if order == 'last_first_comma':
            return ", ".join((p for p in (lastname, firstname) if p))
        elif order == 'first_last':
            return " ".join((p for p in (firstname, middlename, lastname) if p))
        else:
            return " ".join((p for p in (lastname, firstname) if p))

    @api.multi
    @api.depends("firstname", "lastname","middlename")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            record.name = record._get_computed_name(
                record.lastname, record.firstname,record.middlename
            )

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        """Compute the inverted name.

        - If the partner is a company, save it in the lastname.
        - Otherwise, make a guess.

        This method can be easily overriden by other submodules.
        You can also override this method to change the order of name's
        attributes

        When this method is called, :attr:`~.name` already has unified and
        trimmed whitespace.
        """
        # Company name goes to the lastname
        if is_company or not name:
            parts = [name or False, False, False]
        # Guess name splitting
        else:
            order = self._get_names_order()
            # Remove redundant spaces
            name = self._get_whitespace_cleaned_name(
                name, comma=(order == 'last_first_comma'))
            parts = name.split("," if order == 'last_first_comma' else " ", 2)
            if len(parts) == 2:
                if order == 'first_last':
                    parts = [" ".join(parts[1:]), parts[0]]
                else:
                    parts = [parts[0], " ".join(parts[1:])]
            elif len(parts) == 3:
                if order == 'first_last':
                    parts = [" ".join(parts[2:]),parts[1], parts[0]]
            else:
                while len(parts) < 3:
                    parts.append(False)
        return {"lastname": parts[0], "firstname": parts[2], "middlename": parts[1]}

    @api.multi
    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for record in self:
            parts = record._get_inverse_name(record.name, record.is_company)
            record.lastname = parts['lastname']
            record.firstname = parts['firstname']
            record.middlename =  parts['middlename']

    @api.multi
    @api.constrains("firstname", "lastname","middlename")
    def _check_name(self):
        """Ensure at least one name is set."""
        for record in self:
            if all((
                record.type == 'contact' or record.is_company,
                not (record.firstname or record.lastname or record.middlename)
            )):
                raise exceptions.EmptyNamesError(record)
    
    @api.multi
    @api.depends('property_product_pricelist')
    def _get_default_currency(self):
        ### handle the case where the user's company was created after the currency was set
        for rec in self:
            rec.default_currency_id = rec.property_product_pricelist.currency_id
    
    def _set_default_currency(self):
        #raise UserError('{}'.format(self.default_currency_id.name))
        for rec in self:
            if rec.default_currency_id:
                pricelist = self.sudo().env['product.pricelist'].search([('company_id', '=', False), ('currency_id', '=', rec.default_currency_id.id)], limit=1)
                if not pricelist:
                    raise UserError(('Please define a company independent pricelist with currency %s') % rec.default_currency_id.name)
                for company in self.sudo().env['res.company'].search([]):
                    rec.with_context(force_company=company.id).property_product_pricelist = pricelist[0].id
    
    @api.one
    def _get_new_ref(self):
        #we look for the configuration of the company/parent_company of the current contact to build a reference
        if self.company_type == 'company':
            company = self
        else:
            company = self.parent_id
        
        #if no ALTNAME, then we raise an error
        if not company.altname:
            raise ValidationError("Please document an ALTNAME in the {} client sheet to automate refence calculation.".format(company.name))
        
        else:
            reference = "{}-{:03}".format(company.altname, company.core_process_index+1)
            company.core_process_index += 1
            return reference

    
    """
    # NOT OVERWRITE CONTEXT
    @api.one
    def _inverse_product_pricelist(self):
        pls = self.env['product.pricelist'].search(
            [('country_group_ids.country_ids.code', '=', self.country_id and self.country_id.code or False)],
            limit=1
        )
        default_for_country = pls and pls[0]
        actual = self.env['ir.property'].get('property_product_pricelist', 'res.partner', 'res.partner,%s' % self.id)

        # update at each change country, and so erase old pricelist
        if self.property_product_pricelist or (actual and default_for_country and default_for_country.id != actual.id):
            # keep the company of the current user before sudo
            self.env['ir.property'].sudo().set_multi(
                'property_product_pricelist',
                self._name,
                {self.id: self.property_product_pricelist or default_for_country.id},
                default_value=default_for_country.id
            )"""