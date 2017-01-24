# -*- coding: utf-8 -*-
{
    "name": """Project Timelog""",
    "summary": """Track the work time and know what your team is working on""",
    "category": "Project",
    "version": "1.0.0",
    "images": ['images/timelog.png'],
    "author": "IT-Projects LLC, Dinar Gabbasov",
    'website': "https://twitter.com/gabbasov_dinar",
#    "license": "Other proprietary",
    "price": 390,
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
