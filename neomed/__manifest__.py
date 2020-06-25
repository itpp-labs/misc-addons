# Copyright 2020 Artem Kostromin  <https://www.it-projects.info/team/ufaks>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": """НЕОМЕД #1""",
    "summary": """Модуль для учета пациентов""",
    "category": "",
    "images": ["static/description/icon.png"],
    "version": "12.0.1.0.1",
    "application": False,

    "author": "IT-Projects LLC, Kostromin",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "base"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/pacient_view.xml',
        'security/ir.model.access.csv'
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
}
