# -*- coding: utf-8 -*-
{
    "name": """Company-dependent values in System Parameters""",
    "summary": """Adds multi-company support for dozens features""",
    "category": "Extra Tools",
    # "live_test_url": "",
    "images": [],
    "version": "11.0.2.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "LGPL-3",
    "price": 40.00,
    "currency": "EUR",

    "depends": [
        "base_setup",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": 'uninstall_hook',

    "auto_install": False,
    "installable": True,
}
