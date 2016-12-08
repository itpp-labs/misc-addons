=================
 Product Details
=================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

The module adds new fields ``detail_source`` in the ``product.template`` and in the ``stock.production.lot`` models.
To change list of model which contains details you have to inherit the ``_get_detail_source`` function. 
