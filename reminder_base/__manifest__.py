# -*- coding: utf-8 -*-
{
    "name": """Reminders and Agenda (technical core)""",
    "category": "Reminders and Agenda",
    'live_test_URL': 'http://apps.it-projects.info/shop/product/reminders-and-agenda?version=10.0',
    "images": [],
    "version": "1.0.7",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev, Pavel Romanchenko",
    "support": "apps@it-projects.info",
    "website": "https://twitter.com/yelizariev",
    "license": "LGPL-3",
    "price": 9.00,
    "currency": "EUR",

    "depends": [
        "calendar",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/reminder_base_views.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,

    "demo_title": "Reminders and Agenda modules",
    "demo_addons": [
        "reminder_phonecall",
        "reminder_task_deadline",
        "reminder_hr_recruitment",
    ],
    "demo_addons_hidden": [
        "website"
    ],
    "demo_url": "reminders-and-agenda",
    "demo_summary": "The module provides easy way to configure instant or mail notifications for any supported record with date field.",
}
