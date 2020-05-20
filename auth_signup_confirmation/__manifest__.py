# -*- coding: utf-8 -*-
{
    "name": "Confirm SignUp by Email",
    "summary": """New user is able to login only after confirming his/her email""",
    "vesion": "10.0.1.0.1",
    "author": "IT-Projects LLC",
    "website": "https://it-projects.info",
    "images": ["images/auth_signup_confirmation.jpg"],
    "license": "Other OSI approved licence",  # MIT
    "price": 80.00,
    "currency": "EUR",
    "depends": ["auth_signup"],
    "data": ["data/config.xml", "views/thankyou.xml", "data/email.xml"],
    "installable": True,
    "post_init_hook": "init_auth",
}
