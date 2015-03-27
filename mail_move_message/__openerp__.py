{
    'name' : 'Mail relocation',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Social Network',
    'website' : 'https://yelizariev.github.io',
    'price': 9.00,
    'currency': 'EUR',
    'depends' : ['mail'],
    'images': ['images/inbox.png'],
    'data':[
        'mail_move_message_views.xml',
        ],
    'qweb': [
        'static/src/xml/mail_move_message_main.xml',
    ],
    'installable': True
}
