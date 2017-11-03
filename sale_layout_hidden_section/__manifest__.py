# -*- coding: utf-8 -*-
{
    "name": """Hidden Layouts for Sale Orders""",
    "summary": """
        Use layouts within specific Sale Order only""",
    "category": "Sale",
    "images": ['images/sale_layout_hidden_section.png'],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Artyom Losev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "price": 29.00,
    "currency": 'EUR',

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
