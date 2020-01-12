# -*- coding: utf-8 -*-
{
    'name': "Vcls Marketing",

    'summary': """
        VCLS customs marketing module.""",
    'description': """
    """,
    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",
    'category': 'Uncategorized',
    'version': '0.0.1',
    'depends': [
        'project',
        'vcls-project',
        'vcls-crm',
        'vcls_security',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/marketing_views.xml',
    ],
}