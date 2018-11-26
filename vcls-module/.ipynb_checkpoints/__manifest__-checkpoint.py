# -*- coding: utf-8 -*-
{
    'name': "vcls-module",

    'summary': """
        Custom development made by VCLS internal team.""",

    'description': """
        Will contain VCLS customization to be reviewed by the Odoo dev team, such as views, custom fields, custom models or actions.
    """,

    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        
        # VIEWS
        'views/employee.xml', #the VCLS default employee view
        'views/job.xml',
        'views/job_profile.xml',
        'views/contract.xml',
        'views/leave_allocation.xml',
        'views/leave.xml',
        #'views/leave2.xml',
        
        # ACTIONS
        #'actions/hr_employee_automations.xml', 
        
        # MULTISELECTIONS
        'data/hr.diploma.csv',
        #'data/hr.vcls_business_fct.csv', <-- NOW COVERED BY DEPARTMENT MODEL
        'data/hr.project_business_fct.csv',
        'data/hr.project_role.csv',
        'data/hr.vcls_activities.csv',
        'data/hr.department.csv',
        'data/hr.leave.type.csv',
        'data/hr.exceptional.leave.category.csv',
        'data/hr.exceptional.leave.case.csv',
        #'data/hr.job.csv',
        #'data/hr.benefit_type.csv',
        
        # SECURITY
        'security/ir.model.access.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}