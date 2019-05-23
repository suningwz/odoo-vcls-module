# -*- coding: utf-8 -*-
{
    'name': "vcls-project",

    'summary': """
        VCLS customs project module.""",

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
    'depends': [
        'base',
        'project',
        'vcls-crm',
        ],

    # always loaded
    'data': [

        ### SECURITY ###
        'security/vcls_groups.xml',
        #'security/ir.model.access.csv',

        ### VIEWS ###
        'views/dev_project_views.xml',
        'views/dev_task_views.xml',

        ### MENUS ###
        'views/dev_project_menu.xml',
        'views/program_views_menu.xml',

    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}