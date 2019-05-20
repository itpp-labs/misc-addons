# -*- coding: utf-8 -*-
# Copyright 2017 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Project Task To-Do List""",
    "summary": """Use To-Do List to be ensure that all your tasks are performed and to make easy control over them""",
    "category": """Project Management""",
    "images": ['images/todolist_main.png'],
    "version": "8.0.1.1.0",
    "application": False,

    "author": "IT-Projects LLC, Manaev Rafael",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    "price": 69.00,
    "currency": "EUR",

    "depends": ['base', 'project'],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        'views/project_task_subtask.xml',
        'data/subscription_template.xml',
        'security/project_security.xml'
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
