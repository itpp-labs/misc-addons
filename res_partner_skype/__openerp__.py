{
    "name" : "Add skype field to partner info",
    "version" : "0.1",
    "author" : "Ivan Yelizariev",
    "category" : "Base",
    "website" : "https://it-projects.info",
    "description": """
* Add skype field to partner info.
* Add widget skype

    <field name="skype" widget="skype" options="{'type':'call', 'video':0}"/>
	 
    """,
    "depends" : ['web'],
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
    "installable": True
}
