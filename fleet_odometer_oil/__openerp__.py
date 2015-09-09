# -*- coding: utf-8 -*-
{
    'name': "fleet_odometer_oil",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "iledarn",
    'website': "http://www.aviatron-ufa.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
#        'templates.xml',
        'views/fleet_odometer_oil.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo.xml',
    ],
}
