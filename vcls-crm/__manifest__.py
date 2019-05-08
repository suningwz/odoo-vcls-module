# -*- coding: utf-8 -*-
{
    'name': "vcls-crm",

    'summary': """
        VCLS customs for CRM/Sales/Marketing applications.""",

    'description': """
    """,

    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'crm',
                #'marketing_automation',
                #'mass_mailing',
                'website',
                'website_crm',
                'website_crm_score',
                'vcls-contact',
                ],

    # always loaded
    'data': [

        ### SECURITY ###
        #'security/vcls_groups.xml',
        'security/ir.model.access.csv',
        'security/lead_rules.xml',

        ### VIEWS ###
        'views/lead_views.xml',
        #'views/crm_contact_views.xml',

        ### MENUS ###
        'views/lead_menus.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}