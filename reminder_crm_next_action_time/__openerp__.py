# -*- coding: utf-8 -*-
{
    "name": """Reminders and Agenda for Opportunities (with time)""",
    "summary": """Reminders for opportunities with the precise time feature""",
    "category": "Debranding",
    "images": [],
    "version": "1.1.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "website": "https://twitter.com/gabbasov_dinar",
    "license": "GPL-3",
    "price": 21.00,
    "currency": "EUR",

    "depends": [
        "reminder_base",
        "crm",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
