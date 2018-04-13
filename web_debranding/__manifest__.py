# -*- coding: utf-8 -*-
{
    'name': "Backend debranding",
    'version': '10.0.1.0.23',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'Debranding',
    'images': ['images/web_debranding.png'],
    'website': 'https://twitter.com/yelizariev',
    'price': 150.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'mail',
        'web_planner',
        'access_apps',
        'access_settings_menu',
        'mail_base',
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
    'uninstall_hook': 'uninstall_hook',
    'installable': True
}
