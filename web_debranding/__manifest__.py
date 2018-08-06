# -*- coding: utf-8 -*-
{
    'name': "Backend debranding",
    "summary": """Removes references to odoo""",
    'version': '12.0.1.0.24',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'Debranding',
    'images': ['images/web_debranding.png'],
    'website': 'https://twitter.com/yelizariev',
    'price': 250.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'mail',
        'access_settings_menu',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data.xml',
        'views.xml',
        'js.xml',
        'pre_install.xml',
    ],
    'qweb': [
        'static/src/xml/web.xml',
    ],
    "post_load": 'post_load',
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
    'installable': True
}
