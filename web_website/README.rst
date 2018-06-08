.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

=============================
 Website Switcher in Backend
=============================

Technical module to switch Websites in Backend similarly to Company Switcher,
but instead of changing a field in ``res.users`` , it only adds ``website_id``
value to the context.

Also, introduces new fields attribute ``website_dependent``, which can be used
only along with ``company_dependent``. See `<models/test_website.py>`_ and `<tests/test_website_dependent.py>`_ as an example of usage.

Roadmap
=======

* TODO: Use context on switching between websites to allow work with different
  websites at the same time by using different browser tabs.

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
      at `odoo apps store <https://apps.odoo.com/apps/modules/10.0/web_website/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/10.0

HTML Description: https://apps.odoo.com/apps/modules/10.0/web_website/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/misc-addons/commits/10.0/web_website.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/misc-addons/commits/10.0/web_website.atom>`_

Tested on Odoo 10.0 2da4eb58989af1fc0280f5fec12deca2aa6eae88
