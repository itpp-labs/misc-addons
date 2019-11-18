================
 Attachment Url
================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Odoo parameters
===============

* Run Odoo with ``--load=web,ir_attachment_url``
  or set the ``server_wide_modules``
  option in The Odoo configuration file:

::

  [options]
  (...)
  server_wide_modules = web,ir_attachment_url
  (...)

* Note: without the configuration above the module UI wouldn't work - and you couldn't use `@` button on binary image fields to specify their urls manually.
  All other functions of the module will work without the ``--load=...``, e.g. you can still use `ir_attachment_s3` that specifies urls for you in binary image fields.

Usage
=====

* Go to Sales >> Products >> Products
* Open a product
* Upload image to this product or specify image URL
* Save the changes
* Go to Settings >> Technical >> Database Structure >> Attachments
* Open "Advanced Search" (loupe icon)
* In filters set "URL" and custom filter "Resource Field" is set
* See related attachment form that contains URL of the image

Notes
=====
* ``product`` dependency is only required for testing module
