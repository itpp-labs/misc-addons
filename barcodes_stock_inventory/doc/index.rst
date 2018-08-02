===========================================
 Inventory adjustment via barcode scanning
===========================================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way


Usage
=====

* Open menu ``Inventory >> Inventory Adjustment``
* Click ``[Create]`` or select and click ``[Edit]``

  * For inventory creating

    * Type a ``Name``
    * Select Inventoried Location manually or via scanning a barcode of any available location
    * You may continue working with that inventory via clicking the ``[Start Inventory]`` manually or by scanning ``O-CMD.INV`` barcode (see below) or save the created inventory by clicking ``[Save]`` or by scanning barcode ``O-CMD.SAVE`` (see below)

* In order to add product in an inventory, scan its barcode.

  If there are several rows with the same product are presence, the product will be added to a row with the same loaction as `Inventoried Location`, for example:

  `Inventoried Location` is *WH/Stock* and locations of the same product are *WH/Stock/Shelf 1* and *WH/Stock/Shelf 2*
  a new line with the location *WH/Stock* will be added.

* When the work is done click ``[Validate Inventory]``
* Click ``[Save]``

Other operations via barcode scanner
------------------------------------

It's possible to do whole process via barcode scanner only (no mouse, no keyboard, no touchscreen, no whatever). In order to do that, you need to have printed *command barcodes* that contains text code, rather than a product number. List of code and their operations are following:

* O-CMD.INV     - ``[Start Inventory]``
* O-CMD.VALID   - ``[Validate Inventory]``
* O-CMD.SAVE    - ``[Save]`` the inventory

* O-CMD.NEW     - ``[Create]`` new inventory
* O-CMD.EDIT    - ``[Edit]`` inventory

* O-CMD.DISCARD - ``[Discard]`` changes
* O-CMD.CANCEL  - ``[Cancel Inventory]``
* O-CMD.NEXT    - Next inventory in a row
* O-CMD.PREV    - Previous inventory in a row

You can make those barcodes in any barcode generation tool or use prepared ones from ``doc/command-barcodes/`` folder
