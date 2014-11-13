{
    "name" : "Sale reports in russian (KZ)",
    "version" : "0.1",
    "author" : "Ivan Yelizariev",
    "category" : "Sale",
    "website" : "https://it-projects.info",
    "description": """
Добавляет печатные формы:
* накладная

    depends on https://github.com/j2a/pytils
    tested on 8.0 29e08a272c0add31086f7c30ffe154a63e2edf24
    """,
    "depends" : ["stock", "sale_report_ru"],
    "data":[
        'report.xml',
        ],
    "installable": True
}
