{
    "name" : "updates for Money-4 company",
    "version" : "1.0.0",
    "author" : "Ivan Yelizariev",
    "category" : "Base",
    "website" : "https://it-projects.info",
    "sequence": 1,

    "depends" : ["crm", "account", "website", "web"],
    "data":[
        'views.xml',
        'templates.xml',
        ],
    "installable": True,

    "description": """
Calculator form:

    <div id="calculator">
    <select id="x_currency_in_id">
    </select>
    <input id="x_in_amount"></input>
    <select id="x_currency_out_id">
    </select>
    <input disabled="1" id="x_out_amount"></div>
    </div>
    """,
}
