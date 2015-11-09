{
    "name" : "Sale workflow for It-Projects LLC ",
    "version" : "0.1",
    "author" : "IT-Projects LLC, Ivan Yelizariev",
    'license': 'GPL-3',
    "category" : "Hidden",
    "website" : "https://yelizariev.github.io",
    "description": """
    """,
    "depends" : ["sale_stock", "sale_report_ru"],
    "data":[
        'wizard/sale_make_invoice_advance.xml',
        'sale_workflow.xml',
        'sale_view.xml',
        'email_template.xml',
		  'report.xml',
        ],
    "installable": True
}
