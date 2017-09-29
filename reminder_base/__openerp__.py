# -*- coding: utf-8 -*-
{
    'name': "Reminders and Agenda (technical core)",
    'version': '1.0.4',
    'author': 'IT-Projects LLC, Ivan Yelizariev, Pavel Romanchenko',
    'license': 'LGPL-3',
    'category': 'Reminders and Agenda',
    'live_test_url': 'http://apps.it-projects.info/shop/product/reminders-and-agenda?version=9.0',
    'website': 'https://twitter.com/yelizariev',
    'price': 9.00,
    'currency': 'EUR',
    'depends': ['calendar'],
    'data': [
        'reminder_base_views.xml',
    ],
    'installable': True,
    'demo_title': 'Reminders and Agenda modules',
    'demo_addons': ['reminder_phonecall', 'reminder_task_deadline', 'reminder_hr_recruitment'],
    'demo_addons_hidden': ['website'],
    'demo_url': 'reminders-and-agenda',
    'demo_summary': 'The module provides easy way to configure instant or mail notifications for any supported record with date field.',
}
