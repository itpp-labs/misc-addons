# -*- coding: utf-8 -*-
{
    'name': 'Football pitches booking functionality',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Veronika Kotovich',
    'license': 'GPL-3',
    'website': 'https://twitter.com/vkotovi4',
    'category': 'Other',
    'description': """

    """,
    'depends': ['account', 'website_booking_calendar'],
    'data': [
        'views.xml',
        'security/ir.model.access.csv',
        'report_saleorder.xml',
    ],
    'installable': True,
    'auto_install': False,
}
