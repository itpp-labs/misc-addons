# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/molotov>
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """S3 backing up""",
    "summary": """Yet another backup tool, but with sexy graphs""",
    "category": "Backup",
    "images": ["images/odoo-backup.sh.jpg"],
    "version": "13.0.1.0.3",
    "author": "IT-Projects LLC",
    "support": "help@itpp.dev",
    "website": "https://twitter.com/OdooFree",
    "license": "Other OSI approved licence",  # MIT
    "depends": ["iap", "mail"],
    "external_dependencies": {
        "python": ["boto3", "botocore", "pretty_bad_protocol"],
        "bin": [],
    },
    "data": [
        # iap is disabled
        # 'data/odoo_backup_sh_data.xml',
        "security/security_groups.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/odoo_backup_sh_templates.xml",
        "views/odoo_backup_sh_views.xml",
    ],
    "qweb": ["static/src/xml/dashboard.xml"],
    "demo": ["demo/tour_views.xml", "demo/demo.xml"],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": True,
    "application": True,
    "uninstall_hook": "uninstall_hook",
}
