{
    'name' : 'Check mail immediately',
    'version' : '1.0.1',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Social Network',
    'website' : 'https://twitter.com/yelizariev',
    'price': 9.00,
    'currency': 'EUR',
    'depends' : ['base', 'web', 'fetchmail', 'mail'],
    'data': [
        'views.xml',
        ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
    'installable': True
}
