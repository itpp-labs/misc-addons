# -*- coding: utf-8 -*-
# Localization of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ERGOBIT Base',
    'version': '12.0',
    'category': 'Technical Setting',
    'summary': 'Base module for ERGOBIT installations', 
    'description' : """Base module for ERGOBIT installations.""",
    'author' : 'ERGOBIT Consulting',
    'website' : 'http://ergobit.org',
    'depends': ['decimal_precision'],
    'data': [
        'security/ergobase_security.xml',
        'lang/fr_FR.xml',
        'data/ergobase.xml',
        'views/res_partner.xml',
        ],
    'demo': [],
    'qweb': [],
    'test': [],
    'installable': True,
    'auto_install': True,
}

