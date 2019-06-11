.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

====================
 Website debranding
====================

Removes references to odoo.com:

1. *(feature is not required in 12.0+ versions)*
2. Replaces "Odoo" in page title
3. Replaces "Odoo" in help message for empty list. 

   Some list views has word Odoo when search return empty result. E.g. search random string at menu ``[[ Settings ]] >> Users & Companies >> Companies`` that return empty result -- it has Odoo word

    Create and manage the companies that will be managed by **Odoo** from here. Shops or subsidiaries can be created and maintained from here.

4. *(feature is not required in 9.0+ versions)*
5. Deletes *Documentation*, *Support*, *My Odoo.com account*; adds *Developer mode*, *Developer mode (with assets)* links to the top right-hand User Menu.
6. *(feature is not required in 11.0+ versions)*
7. Replaces "Odoo" in Dialog Box

   E.g. try to remove Administrator via menu ``[[ Settings ]] >> Users & Companies >> Users``. It will show warning

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
14. *(feature is not required in 12.0+ versions)*
15. *(feature is not required in 12.0+ versions)*
16. Deletes "Odoo" in a request message for permission desktop notifications (yellow block at ``Discuss`` page). Replaces "Odoo" and icon in desktop notifications
17. [ENTERPRISE] Deletes odoo logo in application switcher
18. Hides Enterprise features in Settings
19. Replaces "Odoo" in all backend qweb templates

    This provides a big part of debranding. You can find examples in any tree view if you click ``[Import]`` button (e.g. at menu ``[[ Settings ]] >> Users & Companies >> Users``), then paste next code in browser javascript console:
    ``$('.oe_import_with_file').removeClass('d-none').siblings('.o_view_nocontent').hide().parent().find('.oe_import_noheaders.text-muted').show()``

     If the file contains the column names, **Odoo** can try auto-detecting the field corresponding to the column. This makes imports simpler especially when the file has many columns.


20. Replaces "odoo.com" in hints, examples, etc.

    For example, when you create new company it shows placeholder for field *Website*

     e.g. www.odoo.com

21. Renames "OdooBot" to "Bot". Use company's logo as bot avatar

    To receive a message from the Bot open menu ``[[ Discuss ]] >> CHANNELS >> #general`` and send ``/help`` to the chat.

22. [ENTERPRISE] Replaces icons for mobile devices with custom url
23. Replaces links to `documentation <https://www.odoo.com/documentation>`__ (e.g. "Help" in Import tool, "How-to" in paypal, etc.) to custom website
24. *(feature is not required in 12.0+ versions)*
25. *(feature is not required in 12.0+ versions)*

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/12.0

HTML Description: https://www.odoo.com/apps/modules/12.0/web_debranding/

Usage instructions: `<doc/index.rst>`__

Changelog: `<doc/changelog.rst>`__


Tested on Odoo 12.0 288662a9de7420deaf7b13c9a8b1b1b92e15ec1f
