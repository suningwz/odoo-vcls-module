# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Formation',
    'category': 'Formation',
    'sequence': 1,
    'summary': 'Organize and schedule your formations ',
    'depends': [
        'base',
    ],
    'description': "",
    'data': [
        'views/formation_views.xml',
        'security/ir.model.access.csv',
    ],
}
