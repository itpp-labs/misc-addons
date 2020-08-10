======================
 Cache Resized Images
======================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

* In browser make following requests:
  * ``/web/image?model=res.users&field=image_128&id=2&width=90&height=90``
  * ``/web/image?model=res.users&field=image_128&id=2&width=100&height=100``
  * ``/web/image?model=res.users&field=image_128&id=2&width=110&height=110``
  * ``/web/image?model=res.users&field=image_128&id=2&width=120&height=120``
* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Go to Settings >> Technical >> Database Structure >> Attachments
* RESULT: you will see resize
