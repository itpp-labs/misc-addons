Backend debranding
==================

Removes references to odoo.com:

1. Deletes Odoo label in footer
2. Replaces "Odoo" in page title
3. Replaces "Odoo" in help message for empty list
4. . 
5. Deletes Documentation, Support, About links
6. Replaces default logo by empty image
7. Replaces "Odoo" in Dialog Box
8. Replaces "Odoo" in strings marked for translation.
9. Replaces default favicon to a custom one
10. **Hides Apps menu** (by default, only admin user see Apps menu. You could change it via tick "Show Modules Menu" in user's access rights tab)
11. Disables server requests to odoo.com (publisher_warranty_url)
12. Deletes "My odoo.com account" button

By default the module replaces "Odoo" to "Software". To configure
module open Settings\\System Parameters and modify

* web_debranding.new_title (put space in value if you don't need Brand in Title)
* web_debranding.new_name
* web_debranding.favicon_url

Further debranding
==================

* open addons/mail/data/mail_data.xml and edit Template "Notification Email" -- delete "using Odoo"
* install **website_debranding** module if module "Website Builder" is installed in your system
* install **pos_debranding** module if module "POS" is installed in your system
* delete "Odoo.com Accounts" record at Settings\\Users\\OAuth Providers if module "OAuth2 Authentication" is installed. in your system
* to debrand **/web/database/manager**:

  * add web_debranding to server wide modules, e.g.

    ./odoo.py --load=web,web_kanban,web_debranding

  * edit addons/web/views/database_manager.html file:

    * delete or modify <title> tag
    * delete or modify favicon
    * delete or modify <img> tag with logo2.png
    * delete or modify paragraph <p>Fill in this form to create an Odoo database...</p>
    * delete or modify warning <div class="alert alert-warning">Warning, your Odoo database ...</div>

Auto-debrand new databases
==========================
To automatically install this module for every new databases set **'auto_install': True** in __openerp__.py files of following modules:

* web_debranding
* mail (built-in)
* base_setup (built-in)
* bus (built-in)


Tested on Odoo 9.0 04c6ee54d86013bc2995778f62074115c1bd9ed3
