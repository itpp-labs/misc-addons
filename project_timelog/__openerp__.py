# -*- coding: utf-8 -*-
{
    "name": """Time Log""",
    "summary": """Time log for project""",
    "category": "Project",
    "version": "1.0.0",

    "author": "IT-Projects LLC, Dinar Gabbasov",
    'website': "https://twitter.com/gabbasov_dinar",
    "license": "GPL-3",

    "depends": [
        #"base",
        "bus",
        "project",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/project_timelog_views.xml",
        "views/project_timelog_templates.xml",
    ],

    "installable": True,
}