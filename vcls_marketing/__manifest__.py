# -*- coding: utf-8 -*-
{
    'name': "VCLS Marketing",

    'summary': """
        VCLS customs marketing module.""",
    'description': """
    """,
    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",
    'category': 'Uncategorized',
    'version': '0.0.8',
    'depends': [
        'project',
        'contacts',
        'vcls-contact',
        'vcls-project',
        'vcls-crm',
        'vcls_security',
        'vcls-expenses',
    ],
    'data': [
        #'security/ir.model.access.csv',
        'views/marketing_views.xml',
    ],
}