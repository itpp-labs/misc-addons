{
    "name": "Barcode Widget",
    "vesion": "13.0.1.0.1",
    "category": "Widget",
    "author": "The Gok Team, IT-Projects LLC",
    # Original module didn't have license information.
    # But App store pages says that it's MIT
    # https://www.odoo.com/apps/modules/9.0/barcode_widget/
    #
    # -- Ivan Yelizariev
    "license": "MIT",
    "depends": ["web"],
    "data": ["views/assets.xml"],
    "qweb": ["static/src/xml/barcode_widget.xml"],
    "js": [],
    "test": [],
    "demo": [],
    "installable": False,
    "application": True,
}
