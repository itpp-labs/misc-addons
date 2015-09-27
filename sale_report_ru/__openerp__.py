{
    "name" : "Sale reports in russian ",
    "version" : "0.1",
    "author" : "IT-Projects LLC, Ivan Yelizariev",
    "category" : "Sales Management",
    "website" : "https://yelizariev.github.io",
    "description": """
    depends on https://github.com/j2a/pytils

    Добавляет печатные формы:

    * договор продаж

    * акт приема-передачи

    * счет (заменяет встроенный отчет)

    * предложение (заменяет встроенный отчет)

    """,
    "external_dependencies": {
        'python': ['pytils']
    },
    "depends" : ["sale", "account", "res_partner_ru", "res_partner_bank_swift"],
    "data":[
        'report.xml',
        'views.xml',
        ],
    "installable": True
}
