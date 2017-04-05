# -*- coding: utf-8 -*-
{
    "name": """Tasks implementation planning""",
    "summary": """Use subtasks to control your tasks""",
    "category": """Project Management""",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Manaev Rafael",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": ['base', 'project'],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        'views/project_task_subtask.xml',
        'data/email_template.xml',
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
