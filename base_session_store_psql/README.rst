.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

==============================
 Store sessions in postgresql
==============================

Odoo uses ``werkzeug.contrib.sessions.FilesystemSessionStore`` that lead to periodic "Session Expired" errors on disributed deployment. Saving sessions in postgresql fixes this issue.

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* Ivan Yelizariev <yelizariev@it-projects.info>
* Christoph Giesel <mail@cgiesel.de>

Further information
===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/9.0/base_session_store_psql/


Tested on `Odoo 9.0 <https://github.com/odoo/odoo/commit/e49893ab2deea0d0be9b1ffcdfae56db1d2fc7c9>`_
