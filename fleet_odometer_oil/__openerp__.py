{
    'name': "Oil odometer field on Vehicle form",

    'summary': """add Last oil change field""",


    'author': "IT-Projects LLC, Ivan Yelizariev",
    'license': 'LGPL-3',
    'website': "https://yelizariev.github.io",

    'category': 'Managing vehicles',
    'version': '0.1',

    'depends': ['base', 'fleet'],

    'data': [
        'views/fleet_odometer_oil.xml',
    ],
    'demo': [
    ],
    'installable': False,
}
