# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em234018>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Website Switcher in Backend""",
    "summary": """Technical module to switch Websites in Backend similarly to Company Switcher""",
    "category": "Hidden",
    # "live_test_url": "",
    "images": [],
    "version": "13.0.3.0.4",
    "application": False,
    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "Other OSI approved licence"  # MIT,
    "price": 15.00,
    "currency": "EUR",
    "depends": ["web", "website", "base_setup"],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/res_users_views.xml",
        "views/ir_property_views.xml",
        "views/assets.xml",
    ],
    "demo": ["demo/assets_demo.xml", "demo/res_users_demo.xml"],
    "qweb": ["static/src/xml/qweb.xml"],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
