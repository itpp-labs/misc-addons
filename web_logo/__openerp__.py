{
    'name' : 'Logo improvements for multicompany',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Tools',
    'website' : 'https://yelizariev.github.io',
    'description': """

Module adds "?company_id=123" to logo url in order to:

* prevent using wrong cached logo
* show correct logo for public users (company_id qcontext variable should be specified)

 Tested on odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends' : ['website', 'web'],
    'data':[
        'views.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
