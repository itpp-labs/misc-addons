{
    'name' : 'Sent mails menu',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://it-projects.info',
    'description': """
Adds "Sent" box. It's the same as archive but filtered by Author.

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d

Further information and discussion: https://yelizariev.github.io/odoo/module/2015/02/19/sentbox.html
    """,
    'depends' : ['mail'],
    'data':[
        'views.xml',
        ],
    'installable': True
}
