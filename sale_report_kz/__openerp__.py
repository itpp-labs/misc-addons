{
    "name" : "Sale reports in russian (KZ)",
    "version" : "0.1",
    "author" : "Ivan Yelizariev",
    "category" : "Sale",
    "website" : "https://yelizariev.github.io",
    "description": """
Добавляет печатные формы:
* накладная

    depends on https://github.com/j2a/pytils
    tested on 8.0 29e08a272c0add31086f7c30ffe154a63e2edf24
    """,
    "external_dependencies": {
        'python': ['pytils']
    },
    "depends" : ["stock", "sale_report_ru", "l10n_ru"],
    "data":[
        'report.xml',
        ],
    "installable": True
}
