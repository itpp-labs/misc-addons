# -*- coding: utf-8 -*-
{
    "name": """Import Holiday ICS""",
    "summary": """
    No need for import holidays manually anymore""",
    "category": "Human Resources",
    "images": ['images/ics_import.png'],
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
