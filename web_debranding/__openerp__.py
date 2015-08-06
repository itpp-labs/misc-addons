{
    'name': "Backend debranding",
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'category': 'Debranding',
    'website': 'https://yelizariev.github.io',
    'price': 90.00,
    'currency': 'EUR',
    'depends': ['web', 'share', 'disable_openerp_online', 'mail_delete_sent_by_footer'],
    'data': [
        'security/web_debranding_security.xml',
        'data.xml',
        'views.xml',
        'js.xml',
        'pre_install.yml',
        ],
    'installable': True
}
