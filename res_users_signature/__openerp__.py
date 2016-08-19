{
    'name': 'Signature templates for user emails',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'Social Network',
    'website': 'https://yelizariev.github.io',
    'depends': ['base'],
    'data': [
        'res_users_signature_views.xml',
        'security/res_users_signature_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': False
}
