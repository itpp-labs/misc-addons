# -*- coding: utf-8 -*-
{
    "name": "Stock Picking Barcode",
    "summary": """Handle Pickings by barcode scanner""",
    "category": "Warehouse",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    'price': 280.00,
    'currency': 'EUR',

    "depends": [
        "stock"
    ],
    "external_dependencies": {"python": [], "bin": []},

    "data": [
        'views/stock.xml',
        'views/stock_view.xml',
        'views/stock_dashboard.xml',
    ],
    "qweb": [
        'static/src/xml/picking.xml',
    ],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
