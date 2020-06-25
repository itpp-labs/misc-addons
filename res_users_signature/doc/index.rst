=====================================
 Signature templates for user emails
=====================================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open signatures ``[ Settings ] >> [ Users and Companies ] >> [ Signatures ]``
* Click ``[ Create ]``
* Fill the fields
* For `properly-showed` signature: in html-editor enter ``'Code View'``-mode by clicking ``"</>"``-icon
* NOTE:
    * Restricted-tags and within them will be erased from message template
    * Leave jinja2-inline-statements in line alone

Allowed html-tags and attributes in template:

    [ <p>, </p>, <img> ]

Template example:

    ---

    <p>${user.name}</p>

    % if user.phone
    <p>${user.phone},</p>
    % endif

    <p>${user.email}</p>

    <p><img src="data:image/jpeg;base64,${user.company_id.logo.decode()}"/></p>

Will be converted to:

    ---

    <p>Bob</p>

    <p>+123456789</p>

    <p>sales@example.com</p>

    <p><img src="data:image/jpeg;base64,ABCDE....12345="/></p>
