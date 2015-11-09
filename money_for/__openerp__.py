{
    "name" : "updates for Money-4 company",
    "version" : "1.0.0",
    "author" : "IT-Projects LLC, Ivan Yelizariev",
    'license': 'GPL-3',
    "category" : "Hidden",
    "website" : "https://yelizariev.github.io",

    "depends" : ["crm", "account", "website", "web", "crm_partner_assign"],
    "data":[
        'views.xml',
        'templates.xml',
        ],
    "installable": True,

    "description": """
Module depends on some website pages, which are not presented on this module.

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
