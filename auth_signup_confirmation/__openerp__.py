# -*- coding: utf-8 -*-
{
    'name': 'Email confirmation on sign up',
    'summary': """New user is able to login only after confirming his/her email""",
    'version': '1.0.0',
    'author': 'IT-Projects LLC',
    'website': "https://twitter.com/OdooFree",
    'license': 'GPL-3',
    'depends': [
        'auth_signup',
    ],
    'data': ['data/config.xml', 'views/thankyou.xml', 'data/email.xml'],
    'installable': True,
    'post_init_hook': 'init_auth',
}
