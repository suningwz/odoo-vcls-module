# -*- coding: utf-8 -*-
{
    'name': "vcls-timesheet",

    'summary': """
        VCLS customs for timesheet applications.""",

    'description': """
    """,

    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_timesheet',
        'vcls-crm',
        'vcls-project',
        ],

    # always loaded
    'data': [
        ### SECURITY ###
        'security/vcls_groups.xml',
        'security/record_rule.xml',
        'security/ir.model.access.csv',
        #'data/parameters.xml',
        ### VIEWS ###
        'views/timesheets_views.xml',
        'actions/timesheet_cron.xml',
        'actions/timesheet_server_action.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}