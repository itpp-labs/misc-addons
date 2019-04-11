{
    "name": """Time Tracker""",
    "summary": """Adds Start/Stop buttons to task work lines. Allows to see statistics on Calendar, Graph, Tree views and more""",
    "category": "Project",
    "images": ["images/timelog.png"],
    "version": "9.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "website": "https://twitter.com/gabbasov_dinar",
    "license": "LGPL-3",
    "price": 390.00,
    "currency": "EUR",

    "depends": [
        "project_issue_sheet",
        "base_action_rule",
        "bus",
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
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": False,
}
