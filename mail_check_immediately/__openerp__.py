{
    'name' : 'Check mail immediately',
    'version' : '0.1',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://yelizariev.github.io',
    'depends' : ['base', 'web', 'fetchmail', 'mail'],
    'data': [
        'views.xml',
        ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
    'installable': True
}
