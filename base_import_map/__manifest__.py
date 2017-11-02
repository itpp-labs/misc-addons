# -*- coding: utf-8 -*-
{
    "name": "Import Settings",
    "version": "1.0.0",
    "summary": "Allows to save import settings to don't specify columns to fields mapping each time.",
    "category": "Extra Tools",
    "images": ["images/icon.png"],

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "website": "https://www.twitter.com/gabbasov_dinar",
    "license": "LGPL-3",
    "price": 90.00,
    "currency": "EUR",

    "depends": ["base_import"],
    "data": [
        "security/ir.model.access.csv",
        "views/base_import_map_templates.xml",
        "views/base_import_map_view.xml",
    ],
    "demo": [
    ],
    "installable": False,
    "auto_install": False,
}
