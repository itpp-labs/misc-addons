.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

================
 Attachment Url
================

The module allows to use url in Binary fields (e.g. in product images) and upload files to external storage (ftp, s3, some web server, etc). It uses url instead of transfer binary data between odoo server and client that allows to reduce the load on server.

Possible incompatibility
========================

* The modules makes monkey patches for ``write``, ``create`` methods of ``fields.Binary``

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* Ildar Nasyrov <iledarn@it-projects.info>

Further information
===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/12.0/ir_attachment_url/


Tested on `Odoo 12.0 <https://github.com/odoo/odoo/commit/46b82f76b68646e24692b4aaee6187b39209c08c>`_
