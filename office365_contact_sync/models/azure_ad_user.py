# See LICENSE file for full copyright and licensing details.
from odoo import models, api, fields

CONTACTS_DATA_DOMAIN = 'contacts/%s'
CONTACTS_CREATE_DOMAIN = 'contacts'
CONTACTS_WEBHOOK_CHANGE_TYPE = 'Deleted,Updated,Created'


class AzureAdUser(models.Model):
    _inherit = 'azure.ad.user'

    contact_delta_link = fields.Char('Delta for Contact Sync')
    contact_sync_use_category = fields.Boolean(string='Only Sync contacts with category', help='Only sync contacts from Outlook to Odoo if they have the specified category.', default=True)
    contact_sync_filter_options = fields.Selection(string='Contacts to Sync', selection=[('manual', 'Manual'), ('all', 'All'), ('filter', 'Filter')], default='manual')
    contact_sync_filters = fields.Many2many(string='Filters', comodel_name='res.partner.filter')

    # ------
    #  CRUD
    # ------
    @api.model
    def default_get(self, default_fields):
        default_fields = super(AzureAdUser, self).default_get(default_fields)

        default_fields['contact_sync_filters'] = [[6, 0, [f.id for f in self.contact_sync_filters.search([]) if f.default_enabled]]]

        return default_fields

    # -------
    # Contact
    # -------
    @api.multi
    def get_not_synced_contacts(self):
        """Get the contacts"""

        self.ensure_one()

        data = []
        at_once = 250

        # Returns a maximum of 5000 contacts
        for i in range(20):
            data_get = self.get_data(domain=CONTACTS_CREATE_DOMAIN + '?$top=%s&$skip=%s' % (at_once, at_once * i))['value']

            data.extend(data_get)

            # Incomplete page returned, get has completed
            if len(data_get) < at_once:
                break

        if self.contact_sync_use_category:
            cat = self.outlook_category

            data = [c for c in data if cat in c['Categories']]

        # TODO Returning all contacts, no just the not synced ones

        return data

    @api.multi
    def get_contact_deltas(self):
        """Returns the last changes to the contacts of the Office 365 user"""

        self.ensure_one()

        if self.partner_id.user_ids and self.partner_id.user_ids.company_id.aad_contact_sync_direction != 'o2a':
            data = self.sync_request(url=self.contact_delta_link, domain=CONTACTS_CREATE_DOMAIN)

            self.contact_delta_link = data[u'@odata.deltaLink']

            return data['value']
        else:
            return []

    @api.one
    def create_contacts(self, contacts):
        """Creates contacts, expects list of tuples. [(Odoo Record, Contact Data), (...),]"""

        outlook_contacts = self.get_not_synced_contacts()

        for contact in contacts:
            # Add Category
            if self.outlook_category:
                contact[1]['Categories'] = contact[1].get('Categories', [])
                contact[1]['Categories'].append(self.outlook_category)
                contact[1]['Categories'] = list(set(contact[1]['Categories']))

            # Check if exists in Outlook with same name and email, but hasn't been synced
            outlook_similar_contacts = []

            for x in outlook_contacts:
                email_1 = x['EmailAddresses'][0].get('Address') if x['EmailAddresses'] else False
                email_2 = contact[1]['EmailAddresses'][0]['Address']
                name_2 = contact[1]['GivenName']

                gn = x['GivenName'] if 'GivenName' in x and x['GivenName'] else False
                mn = x['MiddleName'] if 'MiddleName' in x and x['MiddleName'] else False
                sn = x['Surname'] if 'Surname' in x and x['Surname'] else False

                name_v_1 = ' '.join([p for p in [gn, mn, sn] if p])
                name_v_2 = ' '.join([p for p in [sn, mn, gn] if p])

                if self.filter_similar(email_1=email_1, email_2=email_2, name_1=name_v_1, name_2=name_2) \
                        or self.filter_similar(email_1=email_1, email_2=email_2, name_1=name_v_2, name_2=name_2):
                    outlook_similar_contacts.append(x)

            # Create Link [with existing]
            self.env['azure.ad.user.record.link'].sudo().create({
                'user_id': self.id,
                'create_domain': CONTACTS_CREATE_DOMAIN,
                'data_domain': CONTACTS_DATA_DOMAIN,
                'record': contact[0],
                'data': contact[1],
                'data_id': outlook_similar_contacts[0]['Id'] if outlook_similar_contacts else '',
            })

            # Remove from found contacts so it can't be linked again
            if outlook_similar_contacts:
                outlook_contacts.remove(outlook_similar_contacts[0])

    # -------
    # Helpers
    # -------
    @staticmethod
    def filter_similar(name_1, name_2, email_1, email_2):
        def equal_ignore_case(a, b):
            try:
                return a.lower() == b.lower()
            except AttributeError:
                return a == b

        # Check if name equals, AND email address is empty in one of the contacts, or matching
        if equal_ignore_case(name_1, name_2) and \
                (not email_1 or not email_2 or equal_ignore_case(email_1, email_2)):
            return True

        return False

    # ---------
    # Overrides
    # ---------
    @api.model
    def get_azure_ad_scope(self):
        return super(AzureAdUser, self).get_azure_ad_scope() + ' https://outlook.office.com/contacts.readwrite'

    @api.one
    def init_webhook(self):
        super(AzureAdUser, self).init_webhook()
        # WEBHOOK Re-enable after json/http logic in controller has been implemented

        # self.azure_ad_subscription_ids.create({
        #     'user_id': self.id,
        #     'resource': CONTACTS_CREATE_DOMAIN,
        #     'change_type': CONTACTS_WEBHOOK_CHANGE_TYPE
        # })

    @api.one
    def init_sync(self):
        r = super(AzureAdUser, self).init_sync()

        self.create_contacts(contacts=self.partner_id.get_to_sync_contact_list())

        return r
