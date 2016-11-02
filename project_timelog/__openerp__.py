# -*- coding: utf-8 -*-
{
    "name": """Project timelog""",
    "summary": """Time log for project""",
    "category": "Project",
    "version": "1.0.0",

    "author": "IT-Projects LLC, Dinar Gabbasov",
    'website': "https://twitter.com/gabbasov_dinar",
    "license": "GPL-3",

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
