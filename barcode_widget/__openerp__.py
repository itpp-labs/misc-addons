# -*- coding: utf-8 -*-
{
    'name': 'Barcode Widget',
    'version': '1.0',
    'category': 'Widget',
    'description': """
    Feature:
        - Barcode widget for form view

    How to use:
        - Adding widget="BarCode128" attribute for your Char field on view
        Ex: <field name="barcode" widget="BarCode128" />

    """,
    'author': 'The Gok Team',
    'depends': [
        'web',
    ],

    'data': [
        'views/assets.xml'
    ],

    'qweb': ['static/src/xml/*.xml'],
    'js': [],
    'test': [],
    'demo': [],

    'installable': False,
    'active': False,
    'application': True,
}
