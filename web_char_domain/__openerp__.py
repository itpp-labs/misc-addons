# -*- coding: utf-8 -*-
{
    'name': 'Updated char_domain widget',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category': 'Tools',
    'website': 'https://yelizariev.github.io',
    'description': """
Shows domain value at char_domain widget, e.g.

    7 records selected -> Change selection : [('groups_id', '=', 3)]

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends': ['web'],
    'data': [
        'views.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'installable': True
}
