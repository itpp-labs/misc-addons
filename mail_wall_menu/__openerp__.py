{
    'name' : 'Menu for widgets at Messaging section',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category' : 'Social Network',
    'website' : 'https://yelizariev.github.io',
    'description': """
Module creates special menu at Messaging section to show only gamification-like blocks there.

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends' : ['mail'],
    'data':[
        'mail_wall_menu_views.xml',
        ],
    'installable': False
}
