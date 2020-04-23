# Copyright 2018,2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em234018>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": """Multi-Brand Backend""",
    "summary": """Technical module to switch Websites in Backend similarly to Company Switcher""",
    "category": "Hidden",
    # "live_test_url": "",
    "images": [],
    "version": "13.0.4.0.2",
    "application": False,
    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@itpp.dev",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "LGPL-3",
    # "price": 0.00,
    # "currency": "EUR",
    "depends": ["web", "website", "base_setup"],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/res_users_views.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/ir_property_views.xml",
        "views/assets.xml",
    ],
    "demo": ["demo/assets_demo.xml", "demo/res_users_demo.xml"],
    "qweb": ["static/src/xml/qweb.xml"],
    "post_load": "post_load",
    "pre_init_hook": None,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
