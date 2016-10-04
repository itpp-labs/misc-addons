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
10. **Hides Modules menu** (by default, only admin user see Modules menu. You could change it via tick "Show Modules Menu" in user's access rights tab)
11. Removes odoo.com bindings (via disable_openerp_online module)
12. Deletes "Sent by ... using OpenERP" footer in email (via mail_delete_sent_by_footer module)
13. *(feature is not required in 8.0 version)*
14. *(feature is not required in 8.0 version)*
15. *(feature is not required in 8.0 version)*
16. *(feature is not required in 8.0 version)*
17. *(feature is not required in 8.0 version)*
18. *(feature is not required in 8.0 version)*
19. Replaces "Odoo" in all backend qweb templates (e.g. FAQ in import tool)

By default the module replaces "Odoo" to "Software". To configure
module open Settings\\System Parameters and modify

* web_debranding.new_title (put space in value if you don't need Brand in Title)
* web_debranding.new_name
* web_debranding.favicon_url

Further debranding
==================

* install **website_debranding** module if module "Website Builder" is installed in your system
* uninstall im_odoo_support module.
* delete "Odoo.com Accounts" record at Settings\\Users\\OAuth Providers if module "OAuth2 Authentication" is installed. in your system
* to debrand **/web/database/manager**:

  * add web_debranding to server wide modules, e.g.

	./odoo.py --load=web,web_kanban,web_debranding

  * edit addons/web/views/database_manager.html file:

    * delete or modify <title> tag
    * delete or modify favicon
    * right after script tag with src="/web/static/src/js/boot.js" add code below:
    
          <!-- debranding -->
    
          <script type="text/javascript" src="/web_debranding/static/src/js/main.js"></script>
    
          <script type="text/javascript" src="/web_debranding/static/src/js/title.js"></script>
    
          <script type="text/javascript" src="/web_debranding/static/src/js/about.js"></script>
    
          <script type="text/javascript" src="/web_debranding/static/src/js/dialog.js"></script>
    
          <link href="/web_debranding/static/src/css/database_manager.css" rel="stylesheet"/>

Auto-debrand new databases
==========================
To automatically install this module for every new databases set **'auto_install': True** in __openerp__.py files of following modules:

* web_debranding
* disable_openerp_online
* mail_delete_sent_by_footer
* mail
* base_setup
  

Tested on Odoo 8.0 a40d48378d22309e53e6d38000d543de1d2f7a78

Need our service?
=================

Contact us by `email <mailto:it@it-projects.info>`__ or fill out `request form <https://www.it-projects.info/page/website.contactus>`__:

* it@it-projects.info
* https://www.it-projects.info/page/website.contactus
