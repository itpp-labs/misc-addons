{
    'name': "Resource booking calendar backend",
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'category': 'Sale',
    'website': 'https://yelizariev.github.io',
    'depends': ['website_booking_calendar'],
    'data': [
        'views.xml',
        ],
    'qweb': [
        'static/src/xml/booking_calendar.xml',
    ],
    'installable': True
}
