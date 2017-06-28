# -*- coding: utf-8 -*-
{
    "name": """Sale Layout Hidden Section""",
    "summary": """
        Allows to encapsulate layouts in sale orders.""",
    "category": "Sale",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Artyom Losev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",

    "depends": [
        "sale",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/views.xml'
    ],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
