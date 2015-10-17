{
    'name' : 'Check mail immediately',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'category' : 'Social Network',
    'website' : 'https://yelizariev.github.io',
    'price': 9.00,
    'currency': 'EUR',
    'depends' : ['base', 'web', 'fetchmail', 'mail'],
    'data': [
        'views.xml',
        ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
    'installable': False
}
