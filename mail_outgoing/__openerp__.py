{
    'name' : 'Outgoing mails menu',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category' : 'Social Network',
    'website' : 'https://yelizariev.github.io',
    'description': """
Allows to check outgoing mails, i.e. failed or delayed.

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends' : ['mail'],
    'data':[
        'security/mail_outgoing.xml',
        'security/ir.model.access.csv',
        'mail_outgoing_views.xml',
        ],
    'installable': False
}
