.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

====================
 Website debranding
====================

Removes references to `odoo.com <https://www.odoo.com/>`__:

1. Deletes Odoo label in footer, *i.e.Powered by Odoo*
2. Replaces "Odoo" in page title
3. Replaces "Odoo" in help message for empty list

   Some list views has word Odoo when search return empty result. E.g. search random string at menu ``[[ Settings ]] >> Users & Companies >> Companies`` that return empty result -- it has Odoo word
   Create and manage the companies that will be managed by **Odoo** from here. Shops or subsidiaries can be created and maintained from here.

4. Deletes *Documentation*, *Support*, *My Odoo.com account*; adds *Developer mode*, *Developer mode (with assets)* links to the top right-hand User Menu
5. Replaces default logo by empty image
6. Replaces "Odoo" in Dialog Box

   E.g. try to remove Administrator via menu ``[[ Settings ]] >> Users & Companies >> Users``. It will show Warning
   *You can not remove the admin user as it is used internally for resources created by Odoo (updates, module installation, ...)*

7. Replaces "Odoo" in strings marked for translation

   This provides a big part of debranding. You can find examples at menu ``[[ Settings ]] >> General Settings``:

   * Use external pads in **Odoo** Notes
   * Extract and analyze **Odoo** data from Google Spreadsheet
   * Full list of debranded phrases can be found at menu ``[[ Settings ]] >> Translations >> Application Terms``
   *(You may need to click ``Generate Missing Terms`` first).*

8. Replaces default favicon to a custom one
9. Hides Apps menu

    *By default, only superuser can see Apps menu. You can change it via setting *Apps access* in a user form.*

10. Disables server requests to odoo.com (``publisher_warranty_url``) - optional.

    *Works only for non-enterprise versions of odoo, check* `note <#enterprise-users-notice>`__ *below.*

11. Deletes "My odoo.com account" button
12. Deletes Apps and other blocks from Settings/Dashboard
13. Replaces "Odoo" in planner
14. Replaces footer in planner to a custom one
15. Deletes "Odoo" in a request message for permission desktop notifications (yellow block at ``Discuss`` page). Replaces "Odoo" and icon in desktop notifications
16. [ENTERPRISE] Deletes odoo logo in application switcher
17. Hides Enterprise features in Settings
18. Replaces "Odoo" in all backend qweb templates

    This provides a big part of debranding. You can find examples at menu ``[[ Settings ]] >> Dashboard`` in *Implementation* section
    Follow these implementation guides to get the most out of **Odoo**.

19. Replaces "odoo.com" in hints, examples, etc.

    For example, when you create new company it shows placeholder for field *Website* e.g. www.odoo.com

20. Renames "OdooBot" to "Bot". Use company's logo as bot avatar

    To receive a message from the Bot open menu ``[[ Discuss ]] >> CHANNELS >> #general`` and send ``/help`` to the chat.

21. [ENTERPRISE] Replaces icons for mobile devices with custom url
22. Replaces links to `documentation <https://www.odoo.com/documentation>`__ (e.g. "Help" in Import tool, "How-to" in paypal, etc.) to custom website
23. Removes official videos in planner
24. Replaces "Odoo" in *application installed* mails

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/11.0/web_debranding/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__


Further information
===================

Demo: http://runbot.it-projects.info/demo/website-addons/11.0

HTML Description: https://www.odoo.com/apps/modules/11.0/web_debranding/

Usage instructions: `<doc/index.rst>`__

Changelog: `<doc/changelog.rst>`__

Notifications on updates: `via Atom <https://github.com/it-projects-llc/misc-addons/commits/10.0/web_debranding.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/misc-addons/commits/10.0/web_debranding.atom>`_

Tested on Odoo 11.0 c7171795f891335e8a8b6d5a6b796c28cea77fea
