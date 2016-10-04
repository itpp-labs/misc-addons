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

Credits
=======

Contributors
============
* Ivan Yelizariev <yelizariev@it-projects.info>

Sponsors
========
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

HTML Description: https://apps.odoo.com/apps/modules/8.0/account_invoice_dates/

Usage instructions: `<doc/index.rst>`__

Changelog: `<doc/changelog.rst>`__

Tested on Odoo 8.0 25b1df2eb331275ab6bb5e572665492bbff15bdc
