# -*- coding: utf-8 -*-
{
    "name": """hr public holidays ics import""",
    "summary": """
    import holidays from ics file""",
    "category": "Human Resources",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://it-projects.info",
    "license": "AGPL-3",
    "price": 9.00,
    "currency": "EUR",

    "depends": [
        "hr_public_holidays",
    ],
    "external_dependencies": {"python": ['icalendar'], "bin": []},
    "data": [
        "wizard/import_ics.xml",
        "views/hr_public_holidays_view.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
