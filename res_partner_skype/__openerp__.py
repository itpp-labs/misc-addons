{
    "name" : "Skype field in partner form",
    "version" : "1.0.0",
    "author" : "IT-Projects LLC, Ivan Yelizariev",
    'license': 'LGPL-3',
    "category" : "Tools",
    "website" : "https://yelizariev.github.io",
    'price': 9.00,
    'currency': 'EUR',
    "depends" : ['web'],
    "images": ['images/partner.png'],
    "data":[
        'views.xml',
        'data.xml',
        ],
	 "js":[
		  'static/src/js/skype.js'
		  ],
    "qweb" : [
        'static/src/xml/base.xml',
    ],
    'installable': True
}
