.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

=============================
 Website Switcher in Backend
=============================

Technical module to switch Websites in Backend similarly to Company Switcher. On changing it update field **backend_website_id** in ``res.users``.

Also, introduces new field attribute ``website_dependent``, which can be used
only along with ``company_dependent``. See `<models/test_website.py>`_ and `<tests/test_website_dependent.py>`_ as an example of usage.

Roadmap
=======

* TODO: Use context on switching between websites to allow work with different
  websites at the same time by using different browser tabs. It also fixes
  problem of using superuser's configuration when ``sudo()`` is used.

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__


Further information
===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/10.0/web_website/


Notifications on updates: `via Atom <https://github.com/it-projects-llc/misc-addons/commits/10.0/web_website.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/misc-addons/commits/10.0/web_website.atom>`_

Tested on `Odoo 10.0 <https://github.com/odoo/odoo/commit/2da4eb58989af1fc0280f5fec12deca2aa6eae88>`_
