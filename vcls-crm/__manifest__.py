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
    'version': '1.5.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'crm',
                #'marketing_automation',
                #'mass_mailing',
                'website',
                'website_crm',
                'partner_firstname',
                'website_crm_score',
                'vcls-contact',
                'sale_management',
                'sale_crm',
                'crm_lead_currency',
                'vcls-hr',
                'crm_lead_firstname',
               
                ],

    # always loaded
    'data': [

        ## ACTIONS ##
        # 'actions/cronjob.xml',

        ### SECURITY ###
        #'security/vcls_groups.xml',
        'security/ir.model.access.csv',
        'security/lead_rules.xml',

        ### VIEWS ###
        'views/dropdown_views.xml',
        'views/crm_lead_won_views.xml',
        'views/lead_views.xml',
        'views/partner_relation.xml',
        'views/crm_contact_views.xml',
        'views/product_deliverable_views_menu.xml',
        'views/product_views_menu.xml',
        'views/sale_order_views.xml',
        #'views/sale_order_template_views.xml',

        ### MENUS ###
        'views/lead_menus.xml',
        'views/partner_relation_menus.xml',

        ### RECORDS DATA ###
        'data/partner.relation.type.csv',
        'data/product.pricelist.csv',
        'data/message_subtype.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}