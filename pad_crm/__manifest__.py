# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
{
    "name": """Pad on Leads(Opportunities)""",
    "summary": """Collaborative editing Internal notes + history of changes""",
    "category": "Customer Relationship Management",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=12.0",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "crm",
        "pad",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'crm_lead.xml',
        'template.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "{MODULE_NAME}",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "{SHORT_DESCRIPTION_OF_THE_MODULE}",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
