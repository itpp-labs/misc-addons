Backend debranding
==================

Removes references to odoo.com:

1. Deletes Odoo label in footer, i.e.

    Powered by Odoo     

2. Replaces "Odoo" in page title
3. Replaces "Odoo" in help message for empty list. 

   Some list views has word Odoo when search return empty result. E.g. search random string at menu ``[[ Settings ]] >> Users & Copanies >> Companies`` that return empty result -- it has Odoo word

    Create and manage the companies that will be managed by **Odoo** from here. Shops or subsidiaries can be created and maintained from here.

4. *(feature is not required in 9.0+ versions)*
5. Deletes *Documentation*, *Support*, *My Odoo.com account*; adds *Developer mode*, *Developer mode (with assets)* links to the top right-hand User Menu.
6. *(feature is not required in 11.0+ versions)*
7. Replaces "Odoo" in Dialog Box

   E.g. try to remove Administrator via menu ``[[ Settings ]] >> Users & Copanies >> Users``. It will show warning

    You can not remove the admin user as it is used internally for resources created by **Odoo** (updates, module installation, ...)

8. Replaces "Odoo" in strings marked for translation.

   This provides a big part of debranding. You can find examples at menu ``[[ Settings ]] >> General Settings``:

    Use external pads in **Odoo** Notes

    Extract and analyze **Odoo** data from Google Spreadsheet
   
   Full list of debranded phrases can be found at menu ``[[ Settings ]] >> Translations >> Application Terms`` (You may need to click ``Generate Missing Terms`` first).

9. Replaces default favicon to a custom one
10. **Hides Apps menu**. By default, only superuser can see Apps menu. You can change it via setting *Apps access* in a user form.
11. Disables server requests to odoo.com (publisher_warranty_url) - optional. Works only for non-enterprise versions of odoo, check `note <#enterprise-users-notice>`__ below.
12. *(feature is a part of p.5)*
13. Deletes Share block and branded parts of other blocks at ``[[ Settings ]] >> Dashboard``
14. Replaces "Odoo" in planner
15. Replaces footer in planner to a custom one.
16. Deletes "Odoo" in a request message for permission desktop notifications (yellow block at ``Discuss`` page). Replaces "Odoo" and icon in desktop notifications
17. [ENTERPRISE] Deletes odoo logo in application switcher
18. Hides Enterprise features in Settings
19. Replaces "Odoo" in all backend qweb templates

    This provides a big part of debranding. You can find examples at menu ``[[ Settings ]] >> Dashboard`` in *Implementation* section

     Follow these implementation guides to get the most out of **Odoo**.

20. Replaces "odoo.com" in hints, examples, etc.

    For example, when you create new company it shows placeholder for field *Website*

     e.g. www.odoo.com

21. Renames "OdooBot" to "Bot". Use company's logo as bot avatar

    To receive a message from the Bot open menu ``[[ Discuss ]] >> CHANNELS >> #general`` and send ``/help`` to the chat.

22. [ENTERPRISE] Replaces icons for mobile devices with custom url
23. Replaces links to `documentation <https://www.odoo.com/documentation>`__ (e.g. "Help" in Import tool, "How-to" in paypal, etc.) to custom website
24. Removes official videos in planner
25. Replaces "Odoo" in *application installed* mails

Configuration
=============

By default the module replaces "Odoo" to "Software". To configure
module openf ``[[ Settings ]] >> Technical >> Parameters >> System Parameters`` and modify

* ``web_debranding.new_title`` (put space in value if you don't need Brand in Title)
* ``web_debranding.new_name`` (your Brand)
* ``web_debranding.new_website`` (your website)
* ``web_debranding.new_documentation_website`` (website with documentation instead of official one)
* ``web_debranding.favicon_url``
* ``web_debranding.send_publisher_warranty_url`` - set 0 to disable server requests to odoo.com and 1 otherwise (useful for enterprise contractors). Works only for non-enterprise versions of odoo, check `note <#enterprise-users-notice>`__ below.
* ``web_debranding.planner_footer``
* ``web_debranding.icon_url`` - icon for mobile devices. recommended size :192x192
* ``web_debranding.apple_touch_icon_url`` - icon for IOS Safari. recommended size :152x152


Note. More user friendly way to configure the module is available in `Brand Kit <https://apps.odoo.com/apps/modules/9.0/theme_kit/>`__.

Further debranding
==================

* open addons/mail/data/mail_data.xml and edit Template "Notification Email" -- delete "using Odoo"
* open addons/website_livechat/website_livechat_data.xml and edit in "im_livechat_channel_data_website" record YourWebsiteWithOdoo.com string
* install **website_debranding** module if module "Website Builder" is installed in your system
* install **pos_debranding** module if module "POS" is installed in your system
* delete "Odoo.com Accounts" record at Settings\\Users\\OAuth Providers if module "OAuth2 Authentication" is installed. in your system
* to debrand **/web/database/manager**:

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
* ir_rule_protected
* access_restricted
* access_apps
* access_settings_menu
* mail (built-in)
* base_setup (built-in)
* bus (built-in)

Tested on Odoo 11.0 88ccc406035297210cadd5c6278f6f813899001e

Enterprise users notice
=======================

* `Terms of Odoo Enterprise Subscription Agreement <https://www.odoo.com/documentation/user/9.0/legal/terms/enterprise.html#customer-obligations>`_ don't allow to disable server requests to odoo.com. For this reason feature #11 doesn't work in Enterprise version.

Note
====

* You can also use our new extended `Brand Kit module <https://www.odoo.com/apps/modules/10.0/theme_kit>`_ to brand your odoo instance and create your theme in few clicks.

Need our service?
=================

Contact us by `email <mailto:apps@it-projects.info>`__ or fill out `request form <https://www.it-projects.info/page/website.contactus>`__:

* apps@it-projects.info
* https://www.it-projects.info/page/website.contactus
