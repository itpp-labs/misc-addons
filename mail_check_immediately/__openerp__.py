{
    'name' : 'Check mail immediately',
    'version' : '1.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://yelizariev.github.io',
    'depends' : ['base', 'web', 'fetchmail', 'mail'],
    'data': [
        'views.xml', 'security/ir.model.access.csv'
        ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
    'installable': True
}
