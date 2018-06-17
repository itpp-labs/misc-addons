{
    'name': 'Football pitches booking functionality',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Veronika Kotovich',
    'license': 'LGPL-3',
    'website': 'https://twitter.com/vkotovi4',
    'category': 'Other',
    'depends': ['account', 'website_booking_calendar'],
    'data': [
        'views.xml',
        'security/ir.model.access.csv',
        'report_saleorder.xml',
    ],
    'installable': False,
    'auto_install': False,
}
