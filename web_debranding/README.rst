Website debranding
==================

Removes references to `odoo.com <https://www.odoo.com/>`__:

1. Deletes Odoo label in footer
2. Replaces "Odoo" in page title
3. Replaces "Odoo" in help message for empty list
4. Deletes Documentation, Support, About links. Adds "Developer mode" link to the top right-hand User Menu.
5. Replaces default logo by empty image
6. Replaces "Odoo" in Dialog Box
7. Replaces "Odoo" in strings marked for translation.
8. Replaces default favicon to a custom one
9. **Hides Apps menu** (by default, only admin (superuser) can see Apps menu. You could change it via tick "Show Modules Menu" in user's access rights tab)
10. Disables server requests to odoo.com (publisher_warranty_url) - optional. Works only for non-enterprise versions of odoo, check `note <#enterprise-users-notice>`__ below.
11. Deletes "My odoo.com account" button
12. Deletes Apps and other blocks from Settings/Dashboard
13. Replaces "Odoo" in planner
14. Replaces footer in planner to a custom one.
15. Deletes "Odoo" in a request message for permission desktop notifications. Replaces "Odoo" and icon in desktop notifications
16. [ENTERPRISE] Deletes odoo logo in application switcher
17. Hides Enterprise features in Settings
18. Replaces "Odoo" in all backend qweb templates (e.g. FAQ in import tool)
19. Replaces "odoo.com" in hints, examples, etc.
20. Rename "OdooBot" to "Bot". Use company's logo as bot avatar
21. [ENTERPRISE] Replaces icons for android and apple devices with custom url
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

Further information
===================

Demo: http://runbot.it-projects.info/demo/website-addons/10.0

HTML Description: https://www.odoo.com/apps/modules/10.0/web_debranding/

Usage instructions: `<doc/index.rst>`__

Changelog: `<doc/changelog.rst>`__

Tested on Odoo 10.0 d7b9d141b7c40cfd3f9a53a0aa9e73551ddd01a5

