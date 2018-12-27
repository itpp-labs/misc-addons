{
    'name': 'Barcode Widget',
    'version': '1.0.1',
    'category': 'Widget',
    'author': 'The Gok Team, IT-Projects LLC',
    # Original module didn't have license information.
    # But App store pages says that it's LGPL-3
    # https://www.odoo.com/apps/modules/9.0/barcode_widget/
    #
    # -- Ivan Yelizariev
    'license': 'LGPL-3',
    'depends': [
        'web',
    ],

    'data': [
        'views/assets.xml'
    ],

    'qweb': ['static/src/xml/barcode_widget.xml'],
    'js': [],
    'test': [],
    'demo': [],

    'installable': False,
    'active': False,
    'application': True,
}
