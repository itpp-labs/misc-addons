{
    'name': "Backend debranding",
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'category': 'Debranding',
    'website': 'https://yelizariev.github.io',
    'depends': ['web', 'share'],
    'data': [
        'security/web_debranding_security.xml',
        'data.xml',
        'views.xml',
        'js.xml',
        'pre_install.yml',
        ],
    'installable': True
}
