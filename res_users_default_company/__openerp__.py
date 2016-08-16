# -*- coding: utf-8 -*-
{
    'name': "User's default company",
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category': 'Tools',
    'website': 'https://yelizariev.github.io',
    'description': """
Adds field "default company". It can be used, for example, in Setting / Technical / Parameters / Company defaults.

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends': [],
    'data': [
        'views.xml',
    ],
    'installable': True
}
