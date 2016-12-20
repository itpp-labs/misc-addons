# -*- coding: utf-8 -*-
{
    "name": """Brand kit""",
    "summary": """Brand your odoo instance in few clicks""",
    "category": "Debranding",
    "images": [],
    "version": "1.1.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    "price": 50.00,
    "currency": "EUR",

    "depends": [
        "web_debranding",
        "web_login_background",
        "web_widget_color",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/ir_attachment.xml",
        "views/templates.xml",
        "views/res_config.xml",
        "views/theme.xml",
        "data/theme_data.xml",
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
