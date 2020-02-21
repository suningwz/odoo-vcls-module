# -*- coding: utf-8 -*-
{
    'name': "Mail Activity Kpi",

    'summary': """
        VCLS customs for kpi applications.""",

    'description': """
    """,

    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",
    'category': 'Uncategorized',
    'version': '0.0.1',
    'depends': [
        'mail',
    ],

    'data': [
        ### VIEWS ###
        'views/kpi_views.xml',
        ### SECURITY ###
        'security/ir.model.access.csv'
    ],

    'demo': [
    ],
}
