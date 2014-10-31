{
    'name' : 'Sales in mediation company (custom) ',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Workflow',
    'website' : 'https://it-projects.info',
    'description': """

    """,
    'depends' : ['sale_mediation', 'sale', 'crm', 'project', 'contract_purchases', 'account_analytic_analysis', 'access_custom', 'website_proposal'],
    'data':[
        'report.xml',
        'wizard/sale_case.xml',
        'views.xml',
        #'data.xml',
        ],
    'installable': True,
}
