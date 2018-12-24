# -*- coding: utf-8 -*-
{
    "name": """Time Tracker""",
    "summary": """Adds Start/Stop buttons to task work lines. Allows to see statistics on Calendar, Graph, Tree views and more""",
    "category": "Project",
    "version": "8.0.1.0.1",
    "images": ['images/timelog.png'],
    "author": "IT-Projects LLC, Dinar Gabbasov",
    'website': "https://twitter.com/gabbasov_dinar",
    "license": "GPL-3",
    "price": 189,
    "currency": "EUR",

    "depends": [
        "bus",
        "im_chat",
        "base_action_rule",
        "project_timesheet",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/project_timelog_views.xml",
        "views/res_config_view.xml",
        "views/project_timelog_templates.xml",
        "data/project_timelog_data.xml",
        "data/pre_install.yml",
    ],

    "installable": True,
}
