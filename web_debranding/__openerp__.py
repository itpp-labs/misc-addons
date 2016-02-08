{
    'name': "Backend debranding",
    'version': '1.0.2',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'Debranding',
    'website': 'https://twitter.com/yelizariev',
    'price': 90.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'mail',
        'web_planner',
        'access_apps',
        'access_settings_menu',
    ],
    'data': [
        'security/web_debranding_security.xml',
        'security/ir.model.access.csv',
        'data.xml',
        'views.xml',
        'js.xml',
        'pre_install.yml',
        ],
    'qweb': [
        'static/src/xml/web.xml',
    ],
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'installable': True
}
