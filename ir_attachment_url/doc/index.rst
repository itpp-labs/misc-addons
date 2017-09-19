================
 Attachment Url
================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Odoo parameters
===============

* Add ``ir_attachment_url`` to ``--load`` parameters, e.g.::

    ./openerp-server --load web,ir_attachment_url --config=/path/to/openerp-server.conf

Usage
=====

* Go to Sales >> Products menu
* Open a product
* Upload image to this product or specify image URL
* Save the changes
* Go to Settings >> Database Structure >> Attachments menu
* See related attachment form that contains URL of the image
