# -*- coding: utf-8 -*-
{
    'name': "vcls-suppliers",

    'summary': """
        External Resource Management""",

    'description': """
        External Resource Management
    """,

    'author': "VCLS",
    'website': "https://voisinconsulting.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'survey',
        'vcls-contact',
        ],

    # always loaded
    'data': [
        ### RECORDS
        'data/expertise.area.csv',
        'data/project.supplier.type.csv',

        ### SECURITY
        'security/vcls_groups.xml',
        'security/ir.model.access.csv',

        ### VIEWS
        'views/sup_contact_views.xml',

        ### MENUS
        'views/supplier_menu.xml',  
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}