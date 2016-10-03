===========
 Brand kit
===========

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Install `Website login background <https://apps.odoo.com/apps/modules/9.0/website_login_background/>`__ module too, if you use *website*.

Configuration
=============

* `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`__
* Open menu ``Settings / Brand Kit / Brand``
* Choose **Color Scheme** or create new one. To return default color scheme set empty value
* **Favicon**: type some name (e.g. *favicon*) and click *Create and Edit*

  * Choose **Type** (File or URL), then upload icon or specify url
* Click ``[Apply]``

To temporarly undo Color Scheme (e. g. if you have applied non-contrast background and text colors)

* Open browser console (F12 in Chrome)
* Type and click Enter:

    $('#custom_css').remove()
