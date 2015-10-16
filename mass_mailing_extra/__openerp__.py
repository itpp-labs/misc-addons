{
    'name' : 'Improvements for mass mailing',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'category' : 'Mail',
    'website' : 'https://yelizariev.github.io',
    'description': """
Modules adds:

* partners info in mail.mail.statistics tree
* partners info in mail.mail.statistics form

Tested on 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284
    """,
    'depends' : ['mass_mailing'],
    'data':[
        'views.xml',
        ],
    'installable': False
}
