# -*- coding: utf-8 -*-
{
    "name": """Web preview""",
    "summary": """Web preview""",
    "category": "Web",
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
        "ir_attachment_url",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/web_preview_template.xml",
    ],
    "qweb": [
        "static/src/xml/media_tree_view_widget.xml",
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
