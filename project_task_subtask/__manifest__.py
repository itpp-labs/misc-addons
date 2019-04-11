# Copyright 2017-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017-2018 manawi <https://github.com/manawi>
# Copyright 2017 Karamov Ilmir <https://it-projects.info/team/ilmir-k>
# Copyright 2017-2018 iledarn <https://github.com/iledarn>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Project Task Checklist""",
    "summary": """Use checklist to be ensure that all your tasks are performed and to make easy control over them""",
    "category": """Project Management""",
    "images": ['images/checklist_main.png'],
    "version": "11.0.1.1.0",
    "application": False,

    "author": "IT-Projects LLC, Manaev Rafael",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    "price": 69.00,
    "currency": "EUR",

    "depends": ['base', 'project'],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        'views/project_task_subtask.xml',
        'views/assets.xml',
        'data/subscription_template.xml',
        'security/project_security.xml'
    ],
    "qweb": [
        'static/src/xml/templates.xml'
    ],
    "demo": [
        'demo/project_task_subtask_demo.xml'
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
