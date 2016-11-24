# -*- coding: utf-8 -*-
{
    'name': "Reminders and Agenda for Opportunities (with time)",
    'summary': "Reminders for opportunities with the precise time feature",
    'version': '1.0.0',
    'application': False,
    'author': 'IT-Projects LLC, Dinar Gabbasov',
    'license': 'GPL-3',
    'category': 'Reminders and Agenda',
    'website': 'https://twitter.com/gabbasov_dinar',
    'price': 21.00,
    'currency': 'EUR',
    'depends': ['reminder_base', 'crm'],
    'data': [
        'views.xml',
    ],
    'post_load': None,
    'pre_init_hook': None,
    'post_init_hook': None,

    'auto_install': False,
    'installable': True,
}
