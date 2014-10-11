{
    'name' : 'Website proposal for leads',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://it-projects.info',
    'description': """
Web-based proposals for leads
    """,
    'depends' : ['website_proposal', 'crm'],
    'data':[
        'views.xml',
        'report.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
