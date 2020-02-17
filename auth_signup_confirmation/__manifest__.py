{
    "name": "Email confirmation on sign up",
    "summary": """New user is able to login only after confirming his/her email""",
    "vesion": "13.0.1.0.1",
    "author": "IT-Projects LLC",
    "website": "https://it-projects.info",
    "license": "Other OSI approved licence"  # MIT,
    "price": 40.00,
    "currency": "EUR",
    "depends": ["auth_signup"],
    "data": ["data/config.xml", "views/thankyou.xml", "data/email.xml"],
    "installable": False,
    "post_init_hook": "init_auth",
}
