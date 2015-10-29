{
    'name': "Resource booking calendar backend",
    'version': '1.0.0',
    'author' : 'IT-Projects LLC, Veronika Kotovich',
    'website' : 'https://twitter.com/vkotovi4',
    'category': 'Sale',
    'depends': ['resource', 'sale', 'web_widget_color'],
    'data': [
        'views.xml',
        ],
    'qweb': [
        'static/src/xml/booking_calendar.xml',
    ],
    'installable': True
}
