{
    'name' : 'Basic module for custom security stuff',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://yelizariev.github.io',
    'description': """
See access_custom module as example of usage.

How to create or edit custom groups:

* open Settings\Users\Groups
* select some group "Custom User Groups / ..." or create new one and set value "Custom User Groups" for  "Application" field
* click "edit"
* add or delete inherited groups in "Inherited" tab
* click "save"

How to apply groups for some users:

* open Settings\Users\Users
* select user you need
* click "clear access rights"
* tick access groups you need. In the main, you have to use only ones from "Custom User Groups" sector, because all inherited tick boxes will be ticked automatically, after you click save.
* click save

Please note, that if you make changes in custom groups, then you have to repeat process of applying groups for each related users.

Tested on 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d.
    """,
    'depends' : ['base'],
    'data':['data.xml'],
    'installable': True
}
