.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

====================
 Backend debranding
====================

Build and enhance brand by removing references to `odoo.com <https://www.odoo.com/>`__ and customizing company logo, favicon, page title, etc.

1. (feature is not required in 12.0+ versions)
2. Replaces "Odoo" in page title 
3. Replaces "Odoo" in help message for empty list 
4. (feature is not required in 9.0+ versions)
5. Deletes Documentation, Support, About links. Adds "Developer mode" link to the top right-hand User Menu. 
6. (feature is not required in 11.0+ versions)
7. Replaces "Odoo" in Dialog Box 
8. Replaces "Odoo" in strings marked for translation 
9. Replaces default favicon to a custom one 
10. Hides Apps menu (by default, only Super User can see Apps menu. You could change it via tick "Show Modules Menu" in user's access rights tab. 
11. Disables server requests to odoo.com (publisher_warranty_url) - optional. Works only for non-enterprise versions of odoo 
12. (feature is a part of p.5)
13. Deletes Share block and branded parts of other blocks at [[ Settings ]] >> Dashboard 
14. (feature is not required in 12.0+ versions)
15. (feature is not required in 12.0+ versions)
16. (feature is not required in 12.0+ versions)
17. [ENTERPRISE] Deletes odoo logo in application switcher 
18. Hides Enterprise features in Settings 
19. Replaces "Odoo" in all backend qweb templates (e.g. FAQ in import tool) 
20. Replaces "odoo.com" in hints, examples, etc. 
21. Rename "OdooBot" to "Bot". Use company's logo as bot avatar 
22. [ENTERPRISE] Replaces icons for android and apple devices with custom url 
23. Replaces links to `documentation <https://www.odoo.com/documentation>`__ (e.g. "Help" in Import tool, "How-to" in paypal, etc.) to custom website 
24. (feature is not required in 12.0+ versions)
25. (feature is not required in 12.0+ versions)

Modules that can be disabled
----------------------------

If you don't need functionality of the `access_settings_menu <https://apps.odoo.com/apps/modules/12.0/access_settings_menu/>`__ you can remove it from dependencies in manifest file


Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__


Further information
===================

Odoo Apps Store: https://www.odoo.com/apps/modules/12.0/web_debranding/


Notifications on updates: `via Atom <https://github.com/it-projects-llc/misc-addons/commits/12.0/web_debranding.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/misc-addons/commits/12.0/web_debranding.atom>`_

Tested on `Odoo 12.0 <https://github.com/odoo/odoo/commit/288662a9de7420deaf7b13c9a8b1b1b92e15ec1f>`_
