# -*- coding: utf-8 -*-
{
    "name": """Store sessions in postgresql""",
    "summary": """Fixes "Session Expired" issue in destributed deployment""",
    "category": "Extra Tools",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "website": "https://twitter.com/OdooFree",
    "license": "AGPL-3",

    "depends": [
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": 'post_load',
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
