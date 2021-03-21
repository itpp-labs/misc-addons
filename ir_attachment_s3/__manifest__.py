# -*- coding: utf-8 -*-
{
    "name": """S3 Attachment Storage""",
    "summary": """Upload attachments on Amazon S3""",
    "category": "Tools",
    "images": [],
    "version": "10.0.1.2.1",
    "application": False,
    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://twitter.com/OdooFree",
    "license": "Other OSI approved licence",  # MIT
    "depends": ["ir_attachment_url"],
    "external_dependencies": {"python": ["boto3"], "bin": []},
    "data": [
        "data/ir_attachment_s3_data.xml",
        "views/ir_attachment_s3.xml",
        "security/ir.model.access.csv",
    ],
    "qweb": [],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": True,
}
