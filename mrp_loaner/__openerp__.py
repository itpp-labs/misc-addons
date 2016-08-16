# -*- coding: utf-8 -*-
{
    'name': 'Loaner equipment',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category': 'Custom',
    'website': 'https://yelizariev.github.io',
    'description': """
Allows manage loaner equipment

Tested on Odoo 8.0 ea60fed97af1c139e4647890bf8f68224ea1665b
    """,
    'depends': ['mail', 'mrp'],
    'data': [
        'mrp_loaner_views.xml',
    ],
    'installable': True
}
