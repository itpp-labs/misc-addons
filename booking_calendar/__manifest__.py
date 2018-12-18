{
    'name': "Resource booking calendar backend",
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Veronika Kotovich',
    'license': 'LGPL-3',
    'website': 'https://twitter.com/vkotovi4',
    'category': 'Sale',
    'depends': [
        'resource',
        'sale',
        'web_widget_color',
        'web_calendar_repeat_form',
        'web_calendar_quick_navigation',
        'warning',
        'hr_public_holidays',
    ],
    'data': [
        'views.xml',
        'report_saleorder.xml',
    ],
    'qweb': [
        'static/src/xml/booking_calendar.xml',
    ],
    'installable': False
}
