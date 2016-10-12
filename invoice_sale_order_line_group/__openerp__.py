# -*- coding: utf-8 -*-
{
    "name": """Invoice sale order line group""",
    "summary": """
    The module facilitates the creation one aggregated invoice from chosen order lines. The order lines may be from different sale orders.""",
    "category": "Accounting & Finance",
    "images": ['images/lines_to_invoice.png'],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    "price": 15.00,
    "currency": "EUR",

    "depends": [
        "sale",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/invoice_sale_order_line_group.xml",
        "wizard/create_grouped_invoice.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
