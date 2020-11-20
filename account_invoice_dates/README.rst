.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

===============================================
 Start-End dates in invoice and analytic lines
===============================================

Adds fields
* Start Date
* End Date

to models:
* account.invoice.line
* account.analytic.line

Copies dates from ``account.invoice`` to ``account.analytic.line`` whenever Invoice is validated

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* Ivan Yelizariev <yelizariev@it-projects.info>

* `IT-Projects LLC <https://it-projects.info>`__

  The module is not maintained since Odoo 9.0.

Further information
===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/8.0/account_invoice_dates/


Tested on `Odoo 8.0 <https://github.com/odoo/odoo/commit/25b1df2eb331275ab6bb5e572665492bbff15bdc>`_
