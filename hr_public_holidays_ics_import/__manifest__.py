{
    "name": """Import Holiday ICS""",
    "summary": """
    No need for import holidays manually anymore""",
    "category": "Human Resources",
    "images": ["images/ics_import.png"],
    "version": "11.0.1.0.0",
    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://itpp.dev",
    "license": "Other OSI approved licence",  # MIT
    "price": 9.00,
    "currency": "EUR",
    "depends": ["hr_public_holidays"],
    "external_dependencies": {"python": ["icalendar"], "bin": []},
    "data": ["wizard/import_ics.xml", "views/hr_public_holidays_view.xml"],
    "qweb": [],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": False,
    "auto_install": False,
}
