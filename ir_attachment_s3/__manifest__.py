# -*- coding: utf-8 -*-
{
    "name": """S3 Attachment Storage""",
    "summary": """Upload attachments on Amazon S3""",
    "category": "Tools",
    "images": [],
    "version": "1.1.0",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://it-projects.info",
    "license": "AGPL-3",
    "price": 200.00,
    "currency": "EUR",

    "depends": [
        'ir_attachment_url',
    ],
    "external_dependencies": {"python": ['boto3'], "bin": []},
    "data": [
        "views/ir_attachment_s3.xml",
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
