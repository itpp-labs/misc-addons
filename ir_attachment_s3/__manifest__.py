{
    "name": """S3 Attachment Storage""",
    "summary": """Upload attachments on Amazon S3""",
    "category": "Tools",
    "images": [],
    "version": "11.0.1.2.1",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://it-projects.info",
    "license": "AGPL-3",
    "price": 200.00,
    "currency": "EUR",

    "depends": [
        'base_setup',
        'ir_attachment_url',
    ],
    "external_dependencies": {"python": ['boto3'], "bin": []},
    "data": [
        "data/ir_attachment_s3_data.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
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
