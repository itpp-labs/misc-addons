{
    'name' : 'Translate website_description',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://it-projects.info',
    'description': """

    """,
    'depends' : ['website_partner','website_sale_delivery', 'website_sale', 'website_quote'],
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
