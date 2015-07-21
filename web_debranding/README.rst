Backend debranding
==================

Removes references to odoo.com:

1. Deletes Odoo label in footer
2. Replaces "Odoo" in page title
3. Replaces "Odoo" in help message for empty list
4. Deletes Odoo link (as well as "Manage databases" link) from login page
5. Deletes About Odoo link
6. Replaces default logo by empty image
7. Replaces "Odoo" in Dialog Box
8. Replaces "Odoo" in strings marked for translation.
9. Replaces default favicon to a default one

By default the modules replaces "Odoo" to "Software". To configure
this open Settings\\System Parameters and modify

* web_debranding.new_title (put space in value if you don't need Brand in Title)
* web_debranding.new_name

Tested on Odoo 8.0 eeedd2d9f52d46d8193059854e7430ca0c1fd6c0
