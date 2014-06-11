{
    'name' : 'combination of POS and e-commerce',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://it-projects.info',
    'description': '''
    Customer create order online and buy items offline via order ID.

    ''',
    'depends' : ['point_of_sale', 'website_sale'],
    'data':[
        'views.xml',
        'templates.xml',
        ],
    'qweb': ['static/src/xml/main.xml'],
    'installable': True
}
