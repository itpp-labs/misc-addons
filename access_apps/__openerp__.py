{
    'name': 'Control access to Apps',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'category': 'Tools',
    'website': 'https://twitter.com/yelizariev',
    'price': 10.00,
    'currency': 'EUR',
    'depends': [
        'web_settings_dashboard',
        'access_restricted'
    ],
    'data': [
        'views/access_apps.xml',
        'security/access_apps_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True
}
