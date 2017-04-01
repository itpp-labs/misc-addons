# -*- coding: utf-8 -*-
{
    "name": """Website sale images preview""",
    "summary": """Website sale images preview""",
    "category": "Website",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://twitter.com/gabbasov_dinar",
    "license": "GPL-3",
    # "price": 0.00,
    # "currency": "EUR",

    "depends": [
        "website_sale",
        "web_preview",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/website_sale_images_preview_views.xml",
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
