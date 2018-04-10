# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Purchase Order from Sale Order""",
    "summary": """{SHORT_DESCRIPTION_OF_THE_MODULE}""",
    "category": "Warehouse",
    # "live_test_url": "",
    "images": [],
    "version": "11.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/KolushovAlexandr",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "sale_management",
        "purchase",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "wizard/purchase_order_wizard_form.xml",
        "views/views.xml",
    ],
    "qweb": [
        # "static/src/xml/{QWEBFILE1}.xml",
    ],
    "demo": [
        # "demo/{DEMOFILE1}.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}