# -*- coding: utf-8 -*-
{
    'name': "vcls security",

    'summary': """
        VCLS groups and security.""",
    'description': """
    """,
    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",
    'version': '0.0.1',
    'depends': [
        'base',
        'project',
        'sale',
        'purchase',
        'hr_timesheet',
        'project_forecast',
    ],
    'data': [
        'security/pre_hooks.sql',
        'security/vcls_groups.xml',
        'security/ir.model.access.csv',
        'security/lc_security.xml',
    ],
    'demo': [
    ],
}
