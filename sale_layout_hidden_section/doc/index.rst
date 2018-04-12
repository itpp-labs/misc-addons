================================
 Hidden Layouts for Sale Orders
================================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way


Configuration
=============

* Open ``Sales >> Settings`` menu
* Switch **Sales Reports Layout** to *Personalize the sales orders and invoice report with categories, subtotals and page-breaks*
* Click ``[Apply]``

Usage
=====

* Open ``Sales >> Sale Orders`` menu
* Click ``[Create]``
* Add a product to sale order line
* Create new section in ``Section`` field
RESULT: the section created is available (selectable) for this SO only

Global Section
--------------

At any time you are able to set a section as global at ``Sales >> Configuration >> Report Layout Categories`` menu. It means that the section will be available for all SO created.

Note
----

Once you create new sale order, you need to save it after creating new layout (Section), otherwise layout will not be displayed on other order lines.
