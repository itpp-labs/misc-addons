# Copyright 2015-2017 Ildar Nasyrov <https://it-projects.info/>
# Copyright 2018 Ruslan Ronzhin <https://it-projects.info/team/rusllan/>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Autostaging project task""",
    "summary": """Change stages of tasks automatically after a specified time""",
    "category": "Project",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=11.0",
    "images": ["images/a.png"],
    "version": "12.0.1.0.1",
    "application": False,
    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/",
    "license": "MIT",
    "price": 39.00,
    "currency": "EUR",
    "depends": ["project", "autostaging_base"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["views.xml"],
    "demo": [],
    "qweb": [],
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
