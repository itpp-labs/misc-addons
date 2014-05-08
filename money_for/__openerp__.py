{
    "name" : "updates for Money-4 company",
    "version" : "0.1",
    "author" : "Ivan Yelizariev",
    "category" : "Base",
    "website" : "https://it-projects.info",
    "description": """
Calculator form:

    <div id="calculator">
    <select id="x_currency_in_id">
    </select>
    <input id="x_in_amount"></input>
    <select id="x_currency_out_id">
    </select>
    <div id="x_out_amount"></div>
    </div>
    """,
    "depends" : ["crm", "account", "website"],
    "data":[
		  'views.xml',
        'templates.xml',
        ],
    "installable": True
}
