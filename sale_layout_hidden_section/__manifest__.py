# -*- coding: utf-8 -*-
# Copyright 2017 Artyom Losev
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Separate Layouts for Sale Orders""",
    "summary": """
        Display the layouts (sections) within the Sale Orders they were created for""",
    "category": "Sale",
    "images": ["images/sale_layout_hidden_section.png"],
    "version": "10.0.1.0.0",
    "application": False,
    "author": "IT-Projects LLC, Artyom Losev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "price": 14.00,
    "currency": "EUR",
    "license": "Other OSI approved licence"  # MIT,
    "depends": ["sale"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["views/views.xml"],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": True,
}
