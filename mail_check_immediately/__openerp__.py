{
    'name' : 'Check mail immediately',
    'version' : '1.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Tools',
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
