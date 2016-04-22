{
    'name': "Backend debranding",
    'version': '1.0.5',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category': 'Debranding',
    'website': 'https://twitter.com/yelizariev',
    'price': 150.00,
    'currency': 'EUR',
    'depends': ['web', 'share', 'disable_openerp_online', 'mail_delete_sent_by_footer'],
    'data': [
        'security/web_debranding_security.xml',
        'data.xml',
        'views.xml',
        'js.xml',
        'pre_install.yml',
        ],
    'qweb': [
        'static/src/xml/database_manager.xml',
    ],
    'auto_install': False,
    'installable': True
}
