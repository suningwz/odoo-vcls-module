# -*- coding: utf-8 -*-
{
    'name': "vcls-hr",

    'summary': """
        VCLS customs for human resource applications.""",

    'description': """
    """,

    'author': "VCLS",
    'website': "http://www.voisinconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.10.10',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'contacts',
                'fleet',
                'hr',
                'hr_contract',
                'hr_holidays',
                'mail',
                'snailmail',
               ],

    # always loaded
    'data': [
        
        ############
        # SECURITY #
        ############
        'security/vcls_groups.xml',
        'security/ir.model.access.csv',
        'security/hr_employee_rules.xml',
        'security/hr_lm_rules.xml',
        #'security/hr_head_rules.xml',
        'security/hr_hrglobal_rules.xml',
        'security/hr_hrlocal_rules.xml',
        
        #########
        # VIEWS #
        #########
        'views/employee.xml',
        #'views/employee_security_test.xml',
        'views/bank_holiday.xml',
        'views/bonuses.xml',
        'views/benefits.xml',
        'views/company_org.xml',
        'views/contract.xml',
        'views/job.xml',
        #'views/job_profile.xml',
        'views/working_times.xml',
      
        ###########
        # ACTIONS #
        ###########
        'actions/hr_employee_menu.xml',
        'actions/hr_employee_cronjob.xml',
        'actions/hr_leave_menu.xml',
        
        #############
        # SEQUENCES #
        #############
        'sequences/hr_sequences.xml',
        
        ####################
        # EMAILS TEMPLATES #
        ####################
        'data/user_group_history.xml',
        
        ###################
        # DEFAULT RECORDS #
        ###################
        
        # employee segmentation
        'data/companies.xml',
        'data/hr.department.csv',
        'data/hr.vcls_activities.csv',
        'data/hr.diploma.csv',
        'data/hr.project_business_fct.csv',
        #'data/hr.project_role.csv',
        'data/hr.office.csv',
        'data/hr.employee.category.csv',
        
        #employee contracts etc.
        #'data/hr.benefit_type.csv',
        'data/hr.trial.period.csv',
        'data/hr.contract.type.csv',
        
        # leaves details
        'data/hr.leave.type.csv',
        'data/hr.exceptional.leave.category.csv',
        'data/hr.exceptional.leave.case.csv',
        #'data/hr.job.csv',
  
    ],
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}