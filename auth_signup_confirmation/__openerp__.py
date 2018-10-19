{
    'name': 'Email confirmation on sign up',
    'summary': """New user is able to login only after confirming his/her email""",
    'version': '1.0.1',
    'author': 'IT-Projects LLC',
    'website': "https://it-projects.info",
    'license': 'LGPL-3',
    "price": 80.00,
    "currency": "EUR",
    'depends': [
        'auth_signup',
    ],
    'data': ['data/config.xml', 'views/thankyou.xml', 'data/email.xml'],
    'installable': False,
    'post_init_hook': 'init_auth',
}
