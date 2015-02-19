{
    'name' : 'Website proposal for leads',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://yelizariev.github.io',
    'description': """
Web-based proposals for leads
    """,
    'depends' : ['website_proposal', 'crm', 'sale_crm', 'sale',],
    'data':[
        'views.xml',
        'report.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
