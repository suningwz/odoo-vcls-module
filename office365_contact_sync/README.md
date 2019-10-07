# Odoo Outlook Contact Sync
Synchronisation between Outlook and Odoo contacts.

## Options
- Only Sync contacts with category: Selecting this option will ensure that only Outlook contacts who have received this category will be synced. This prevents Odoo from synchronising contacts who already exist in your Office account.
- Synchronisation filter: Determines which contacts need to be synced. These settings can be changed after starting the synchronisation, but only newly created items will respect these changes.

## Synced Fields
### Odoo - Outlook
name        <->     Name
title       <->     Title (Only if the title exists in Odoo, otherwise it gets appended to the name of the person)
email       <->     Address + Name
function    <->     JobTitle
parent_id   -->     CompanyName
phone       <->     BusinessPhones
mobile      <->     MobilePhone1
street      <->     Street
city        <->     City
zip         <->     PostalCode
state_id    -->     State
country_id  -->     CountryOrRegion

Company Changes should be done in Odoo or on the Company contact in Outlook

## Supported Actions
### Outlook
- Creating Contacts. Selecting the "Only sync contacts with category" option on sync start will ensure that only contacts who have received the specified category will synchronize.
- Changing Contacts. 

- Deleting Contacts. Only removes the synchronisation with Outlook. The contact will still exists in Odoo. Making changes in Odoo will no longer appear in Outlook.
- Category Removal. If the "Only sync contacts with category" option was checked on sync start, removing the category will stop synchronisation between Outlook and Odoo for the changed contact.

## Sync Start
Starting the synchronisation will link contacts in your outlook account with those in Odoo, creating new ones where necessary, while respecting the options you chose before starting the synchronisation.

## Sync Stop
Logging out of your Office account in Odoo will stop the synchronisation, but will not delete any items. Items created by in your Office account by Odoo will not be removed.