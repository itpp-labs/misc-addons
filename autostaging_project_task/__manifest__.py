# -*- coding: utf-8 -*-
{
    "name": "Autostaging project task",
    "summary": "Change stages of tasks automatically after a specified time",
    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@itpp.dev",
    "license": "Other OSI approved licence",  # MIT
    "website": "https://twitter.com/OdooFree",
    "images": ["images/a.png"],
    "category": "Project",
    "version": "10.0.1.0.1",
    "application": False,
    "depends": ["project", "autostaging_base"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["views.xml"],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": True,
}
