# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class CountryGroup(models.Model):
    _inherit = 'res.country.group'

    tags = fields.Selection([
        (1, 'BD'),
        (2, 'Other')],
        string='Status',
        track_visibility='onchange',
        default=2,
    ) 

class ContactExt(models.Model):

    _inherit = 'res.partner'
    
    ### CUSTOM FIELDS FOR EVERY KIND OF CONTACTS ###

    description = fields.Text()

    hidden = fields.Boolean(
        string="Confidential",
        default=False,
    )

    is_internal = fields.Boolean(
        string="Is Internal",
        compute = '_compute_is_internal',
        store = True,
        default = False,
    )
    
    stage = fields.Selection([
        (1, 'Undefined'),
        (2, 'New'),
        (3, 'Verified'),
        (4, 'Outdated'),
        (5, 'Archived')], 
        string='Status',
        track_visibility='onchange',
        default=1,
    )

    sharepoint_folder = fields.Char(
        string = 'Sharepoint Folder',
        compute = '_compute_sharepoint_folder',
        readonly = True,
    )
    
    custom_sp_link = fields.Char(
        string = 'Custom Sharepoint Folder',
    )

    create_folder = fields.Boolean(
        string = "Create Sharepoint Folder",
    )

    #Contact fields
    fax = fields.Char()

    ### CLIENT RELATED FIELDS ###

    #override to rename
    user_id = fields.Many2one(
        'res.users',
        string = 'Account Manager',
    )

    #BD fields
    country_group_id = fields.Many2one(
        'res.country.group',
        string = "Geographic Area",
        compute = '_compute_country_group',
    )

    #project management fields
    assistant_id = fields.Many2one(
        'res.users',
        string = 'Project Assistant',
    )

    #finance fields
    controller_id = fields.Many2one(
        'res.users',
        string = 'Project Controller',
    )

    invoice_admin_id = fields.Many2one(
        'res.users',
        string = 'Invoice Administrator',
    )

    #connection with external systems
    altname = fields.Char(
        string = 'AltName',
    )


    ###################
    # COMPUTE METHODS #
    ###################
    
    @api.depends('employee')
    def _compute_is_internal(self):
        for contact in self:
            if contact.employee or self.env['res.company'].search([('partner_id.id','=',contact.id)]):
                contact.is_internal = True
    
    @api.depends('country_id')
    def _compute_country_group(self):
        for contact in self:
            groups = contact.country_id.country_group_ids.filtered([('tags','=','1')])
            if groups:
                contact.country_group_id = groups[0]

    @api.depends('category_id','create_folder','altname')
    def _compute_sharepoint_folder(self):
        for contact in self:
            #search if this is an account contact
            if self.env.ref('vcls-contact.category_account') in contact.category_id and contact.create_folder:
                root = self.env.ref('vcls-contact.conf_path_sp_client_root').value
                contact.sharepoint_folder = "{}{:.1}/{}".format(root,contact.altname,contact.altname)
            #raise ValidationError("{}".format(contact.sharepoint_folder))
                

    # We reset the number of bounced emails to 0 in order to re-detect problems after email change
    @api.onchange('email')
    def _reset_bounce(self):
        for contact in self:
            contact.message_bounce = 0