{
    'name': "Resource booking calendar backend",
    'version': '1.0.0',
    'author' : 'IT-Projects LLC, Veronika Kotovich',
    'license': 'GPL-3',
    'website' : 'https://twitter.com/vkotovi4',
    'category': 'Sale',
    'depends': ['resource', 'sale', 'web_widget_color'],
    'data': [
        'views.xml',
        'report_saleorder.xml',
        ],
    'qweb': [
        'static/src/xml/booking_calendar.xml',
    ],
    'installable': True
}
