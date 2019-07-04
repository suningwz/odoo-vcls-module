# -*- coding: utf-8 -*-
{
    'name': "vcls-invoicing",

    'summary': """
        VCLS customs invoicing module.""",

    'description': """
    """,

    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'vcls-hr',
                'vcls-crm',
                'account',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_views.xml',
        'views/invoice_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}