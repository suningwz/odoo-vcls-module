# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Web Gantt Days off',
    'description': """
Web Gantt chart view.
=============================
Usage:
    In order to have weekend days colored (disabled) in gant view 
    colored add gantt_colored_weekend as a key to the action context
    example in an action add <field name="context">{'gantt_colored_weekend':1}</context>

""",
    'depends': ['web_gantt'],
    'data': [
        'views/web_gantt_templates.xml',
    ],
}
