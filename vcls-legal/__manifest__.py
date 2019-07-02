# -*- coding: utf-8 -*-
{
    'name': "vcls-legal",

    'summary': """
        VCLS customs for legal / contract.""",

    'description': """
    """,

    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['agreement_legal',
                'agreement_sale',
                'agreement_legal_sale',
                'vcls-crm',
                ],

    # always loaded
    'data': [
        ### VIEWS ###
        'views/lead_views.xml'
    ],
}
