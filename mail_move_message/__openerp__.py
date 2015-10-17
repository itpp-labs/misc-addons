{
    'name' : 'Mail relocation',
    'version' : '1.0.2',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'category' : 'Social Network',
    'website' : 'https://yelizariev.github.io',
    'price': 9.00,
    'currency': 'EUR',
    'depends' : ['mail', 'web_polymorphic_field'],
    'images': ['images/inbox.png'],
    'data':[
        'mail_move_message_views.xml',
        'data/mail_move_message_data.xml',
        ],
    'qweb': [
        'static/src/xml/mail_move_message_main.xml',
    ],
    'installable': False
}
