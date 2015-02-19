{
    'name' : 'Move message to thread',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Custom',
    'website' : 'https://yelizariev.github.io',
    'description': """
Module allows move message to any thread. For example, customer send message to salesperson's alias. Then salesperson is able to move such private message to lead thread.

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends' : ['mail'],
    'data':[
        'mail_move_message_views.xml',
        ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True
}
