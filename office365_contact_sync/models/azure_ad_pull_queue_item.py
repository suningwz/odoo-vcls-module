# See LICENSE file for full copyright and licensing details.
import json
import re
import traceback

from .azure_ad_user import CONTACTS_CREATE_DOMAIN, CONTACTS_DATA_DOMAIN
from odoo import api, models


class AzureAdPullQueueItem(models.Model):
    _inherit = 'azure.ad.pull.queue.item'

    # ---------
    # Overrides
    # ---------
    @api.one
    def process(self, updated=0):
        if self.domain == 'contacts' or not self.domain:
            try:
                updated += sum(self.process_contact_pull())
            except Exception as e:
                traceback.print_exc()

        return super(AzureAdPullQueueItem, self).process(updated)

    # ----------
    # Delta Pull
    # ----------
    @api.one
    def process_contact_pull(self):
        data = self.user_id.get_contact_deltas()

        updated_count = 0

        for contact in data:
            updated_count += self._process_contact(contact)

        return updated_count

    def _process_contact(self, contact):
        record_link_obj = self.sudo().env['azure.ad.user.record.link']

        should_check_category = self.user_id.contact_sync_use_category
        has_category = self.user_id.outlook_category in contact[u'Categories'] if u'Categories' in contact else False
        is_deleted = u'id' in contact and u'reason' in contact and contact[u'reason'] == 'deleted'

        # If record is deleted or if category required and not on contact, remove possible link
        if is_deleted or (should_check_category and not has_category):
            data_id = re.search(r"'(.+)'", contact['id']).groups()[0] if is_deleted else contact['Id']

            record_link_obj.search([('data_id', '=', data_id)]).unlink()

            return 1
        # Else Patch or Create
        else:
            # Could be multiple links if multiple users connected the same account
            links = record_link_obj.search([('data_id', '=', contact['Id'])])

            partner_fields = self.env['res.partner'].extract_contact_fields(contact)

            # Link exists
            if links:
                # Record has not been deleted, add ChangeQueueItem
                for link in links:
                    if link.record:
                        patch_fields = link.record.extract_changed(partner_fields)

                        # Patch
                        if len(patch_fields):
                            self.sudo().env['azure.ad.change.queue.item'].create({
                                'change': json.dumps(patch_fields),
                                'time': contact['LastModifiedDateTime'],
                                'record': 'res.partner,%s' % link.record.id,
                            })

                            return 1

            # Link does not exists, means new contact in Outlook that has been synced
            else:
                # Check name, don't care about order, capitals and special characters and if email is available match it
                # Check if record with same name and email exists
                domain = [('name', '=ilike', partner_fields['name'])]

                if partner_fields['email'] != '':
                    domain.append(('email', '=like', partner_fields['email']))

                # Get similar contact
                partner = self.env['res.partner'].search(domain, order='create_date DESC')

                # Check if unique similar not synced contact exists
                is_existing_without_link = partner and not record_link_obj.search([('record', '=', 'res.partner,%s' % partner[0].id), ('user_id', '=', self.user_id.id)])

                # Unique similar not synced contact does not exists
                if not is_existing_without_link:
                    # Create new contact, creates links to AzureADUsers
                    partner = self.env['res.partner'].create(partner_fields)

                # Force link creation, link could exists now, created by logic above, logic for handling that in link create function
                record_link_obj.create({
                    'user_id': self.user_id.id,
                    'create_domain': CONTACTS_CREATE_DOMAIN,
                    'data_domain': CONTACTS_DATA_DOMAIN,
                    'record': 'res.partner,%s' % partner[0].id,
                    'data': partner[0].get_azure_ad_contact(),
                    'data_id': contact['Id']
                })

                return 1

            return 0
