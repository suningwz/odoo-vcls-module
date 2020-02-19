# -*- coding: utf-8 -*-
{
    'name': "Disable customers auto-follow",

    'summary': """
Disable or allow automatic record following for customers and suppliers.
    """,

    'description': """
* Disable automatic adding customers and suppliers as followers to odoo records.
* Adds a new menu under Settings -> Email -> Customer auto follow Models
to allow automatic adding suppliers/customers as followers under certain odoo models.
* Adding new customers/suppliers followers remains always possible through the "Add follower" button 
as it is considered a manual action.
* Technically, adding a customer or a customer as follower can be permitted by simply adding   
{'allow_auto_follow': True} to the context. 
    """,

    'author': "Voisin Consulting",
    'website': "http://www.voisinconsulting.com",
    'version': '0.0.2',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_model.xml',
        'views/templates.xml',
    ],
}