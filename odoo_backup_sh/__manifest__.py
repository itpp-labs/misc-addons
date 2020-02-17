# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/molotov>
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """S3 backing up""",
    "summary": """Yet another backup tool, but with sexy graphs""",
    "category": "Backup",
    # "live_test_url": "",
    "images": ["images/odoo-backup.sh.jpg"],
    "version": "11.0.1.0.2",
    "author": "IT-Projects LLC",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/11.0/odoo_backup_sh/",
    "license": "MIT",
    # "price": 1.00,
    # "currency": "EUR",
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
