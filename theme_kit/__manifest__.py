
{
    "name": """Brand kit""",
    "summary": """Brand your odoo instance in few clicks""",
    "category": "Debranding",
    "live_test_url": "http://apps.it-projects.info/shop/product/theme-kit?version=11.0",
    "images": ['images/brandkit.png'],
    "version": "1.1.2",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    "price": 50.00,
    "currency": "EUR",

    "depends": [
        "web_debranding",
        "web_login_background",
        "web_widget_color",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/ir_attachment.xml",
        "views/templates.xml",
        "views/res_config.xml",
        "views/theme.xml",
        "data/theme_data.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,

    "demo_title": "Brand kit",
    "demo_addons": [
        "web_debranding",
        "web_login_background",
    ],
    "demo_addons_hidden": [
    ],
    "demo_url": "theme-kit",
    "demo_summary": "Brand your odoo instance in few clicks.",
    "demo_images": [
        "images/brandkit.png",
    ]
}
