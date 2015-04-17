Basic module for custom security stuff
======================================

The module creates special category "Custom User Groups" and puts access groups of that category to the top of "Access Rights" tab of user form. It helps to manage user roles via creating custom group that is collection of a technical groups.

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

*See access_custom module as example of usage.*

Tested on 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d.
