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
9. Replaces default favicon to a custom one
10. Hide Modules menu (to do it tick "Show Settings Menu" and untick "Show Modules Menu" in user's access rights tab)
11. Removes odoo.com bindings (via disable_openerp_online module)
12. Deletes "Sent by ... using OpenERP" footer in email (via mail_delete_sent_by_footer module)

By default the module replaces "Odoo" to "Software". To configure
module open Settings\\System Parameters and modify

* web_debranding.new_title (put space in value if you don't need Brand in Title)
* web_debranding.new_name
* web_debranding.favicon_url

Further debranding
==================

* install **website_debranding** module if module "Website Builder" is installed. in your system
* uninstall im_odoo_support module.
* delete "Odoo.com Accounts" record at Settings\\Users\\OAuth Providers if module "OAuth2 Authentication" is installed. in your system

Tested on Odoo 8.0 eeedd2d9f52d46d8193059854e7430ca0c1fd6c0
