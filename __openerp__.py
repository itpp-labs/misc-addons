# -*- coding: utf-8 -*-
{
    "name": "Stock Picking Barcode",
    "summary": """Allow check products by barcode""",
    "category": "Warehouse",
    "images": [],
    "version": "9.0.1.0.0",

    "author": "IT-Projects LLC, Pavel Romanchenko, Odoo Community Association (OCA)",
    "website": "https://it-projects.info",
    "license": "AGPL-3",
    # 'price': 9.00,
    # 'currency': 'EUR',

    "depends": [
        "stock"
    ],
    "external_dependencies": {"python": [], "bin": []},

    "data": [
        'security/stock_security.xml',
        'security/ir.model.access.csv',
        'stock_view.xml',
        'product_view.xml',
        'views/report_package_barcode.xml',
        'views/report_lot_barcode.xml',
        'views/report_location_barcode.xml',
        'views/report_stockpicking.xml',
        'views/stock.xml',
    ],
    "qweb": [],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
