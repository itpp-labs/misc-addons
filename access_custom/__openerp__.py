{
    'name' : 'Custom security stuff',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Tools',
    'website' : 'https://yelizariev.github.io',
    'description': """

Tested on 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d.
    """,
    'depends' : ['access_base',
                 'res_users_clear_access_rights',
                 'base',
                 'account',
                 'sale',
                 'crm',
                 'hr_payroll',
                 'hr_expense',
                 'hr_timesheet',
                 'hr_timesheet_sheet',
                 'project',
                 'purchase',
                 'hr_recruitment',
                 'hr_holidays',
                 'hr_evaluation',
                 'board',
                 'marketing',
                 'account_analytic_analysis',
                 'is_employee',
             ],
    'data':[
        'views.xml',
        'security.xml',
        'ir.model.access.csv',
        ],
    'demo':[
        'demo.xml'
    ],
    'installable': True
}
