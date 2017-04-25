=============
 Web Preview
=============

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Odoo parameters
===============

* Add ``ir_attachment_url`` to ``--load`` parameters, e.g.::

    ./openerp-server --load web,ir_attachment_url --config=/path/to/openerp-server.conf

Usage
=====

* Go to ``Sales >> Products`` menu
* Open a product
* Go to the ``Documents`` tab
* Click on image (Browser opens image in popup)
* Click on doc/docx or xls/xlsx file(The file will be downloaded)
* Click on the PDF file (The file will be opened in a new window using the browser built-in viewer)
* Click on the YouTube or Vimeo file (Browser opens video in popup)
