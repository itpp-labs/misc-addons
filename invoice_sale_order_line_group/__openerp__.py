{
    "name": """Invoice multiorder lines""",
    "summary": """Choose different sale order lines from list and create one invoice per partner from them""",
    "category": "Accounting",
    "images": ['images/lines_to_invoice.png'],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    "price": 50.00,
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

    "auto_install": False,
    "installable": False,
}
