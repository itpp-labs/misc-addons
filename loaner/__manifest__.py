{
    "name": """Corsa DRM Loaner""",
    "summary": """The base module for managing loaner""",
    "category": "Sales",
    "images": [],
    "version": "1.0.0",
    "application": False,
    "depends": [
        'stock',
        'product_details',
        'drm_product_attributes',
        'major_unit',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/loaner_security.xml',
        'views/product_views.xml',
    ],
    "qweb": [
    ],
    "demo": [
        # 'data/product_demo.xml',
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
