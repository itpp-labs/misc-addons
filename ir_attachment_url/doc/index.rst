================
 Attachment Url
================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

* Set an avatar for the current user
* `Log in as superuser <https://odoo-development.readthedocs.io/en/latest/odoo/usage/login-as-superuser.html>`__
* Go to Settings >> Technical >> Database Structure >> Attachments
* Below "Search" field click Filters >> Add custom filter >> "Resource field" "is equal to" "image_128"
* Scroll down and find the avatar you have set. Click on it.
* Click on "Edit"
* To URL field paste url to any picture on external resource
* Click on "Save" and reload the page
* RESULT: you will see that the avatar of the user has been changed to that pasted picture

ir_attachment_url_fields context
--------------------------------

In order to store urls instead of binary data in binary fields, you can use ``ir_attachment_url_fields`` context.
For example, you need to create ``res.country`` record which has ``image`` fields, defined as `Binary field <https://github.com/odoo/odoo/blob/d515e4233a009250f41e8a1c1b02235685a69532/odoo/addons/base/models/res_country.py#L58>`__.
To store url to `image` field you need to define context ``ir_attachment_url_fields=res.country.image`` and set value of the field. See `test cases <../tests/test_attachment_fields.py>`__ as detailed examples.

In order to store multiple fields as urls, define context like this ``ir_attachment_url_fields=model.name.field1,another.model.name,field2``.
