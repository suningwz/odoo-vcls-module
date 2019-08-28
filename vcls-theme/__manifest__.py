# -*- coding: utf-8 -*-
{
    'name': "vcls-theme",

    'summary': """
        VCLS custom theme""",

    'description': """
    """,

    'author': "VCLS",
    'website': "https://voisinconsulting.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 
                'web',
                'vcls-crm',
                'vcls-suppliers',
                'vcls-timesheet',
                'vcls-project',
                'vcls-invoicing',
            ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/colors.xml',
        'views/bd_menus.xml',
        'views/rm_menus.xml',
        'views/lc_menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}