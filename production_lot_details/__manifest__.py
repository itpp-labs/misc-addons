# Copyright 2017 Stanislav Krotov <https://www.it-projects.info/team/ufaks>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": """Production Lot Details""",
    "summary": """Allows to add links with details for production lots.""",
    "category": "Extra Tools",
    "images": ["static/description/icon.png"],
    "version": "11.0.1.0.0",
    "application": False,
    "author": "IT-Projects LLC, Ivan Yelizariev",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",
    "depends": ["stock", "base_details"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["data/security_demo.xml", "views/production_lot_detail.xml"],
    "qweb": [],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": False,
}
