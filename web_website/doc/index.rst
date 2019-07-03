=============================
 Website Switcher in Backend
=============================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* As this is a technical module, consider to install other modules that use this one, for example `ir_config_parameter_multi_company <https://apps.odoo.com/apps/modules/11.0/ir_config_parameter_multi_company/>`_

Configuration
=============

Activate **Multi Websites for Backend**:

* Either via ``[[ Settings ]] >> General Settings``
* or per user via ``[[ Settings ]] >> Users >> Users`` (you need to activate `Developer mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__ first)

Usage
=====

Website Switcher
----------------
Once you activated **Multi Websites for Backend**, will see *Website Switcher* in top right-hand corner.

Technically, it changes value of a technical field at User record. It means, that you can work only with one website in a moment, you cannot use two different browser tabs/windows to work with a different websites.

Company Properties
------------------
Via menu ``[[ Settings ]] >> Technical >> Parameters >> Company Properties`` (available in `Developer mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__) you can find exact values for *Website-dependent* fields. The menu shows normal *Company-dependent* fields too. To filter them out use new filter *Website-dependent*.

How it works
~~~~~~~~~~~~

For a given record field and context (Company, Website), priority of the *properties* to be used as field's value is as following:

#. **Website** and **Resource** are matched
#. **Website** is matched, **Resource** is empty
#. **Company** and **Resource**  are matched, **Website** is empty
#. **Company** is matched, **Resource** and **Website** are empty
#. **Company**, **Resource** and **Website** are empty (i.e. only **Field** is matched)

Note, that when **Company** and **Website** are both set, **Website**'s Company
must be equal to **Company** or Empty. Otherwise such records are ignored.

On computing non-website specific (*All Website* option and not ``website_id``
in context) it works as without the module, i.e.:

#. **Company** and **Resource**  are matched
#. **Company** is matched, **Resource** is empty
#. **Company** and **Resource** are empty (i.e. only **Field** is matched)


Note, if some code use ``sudo()`` before getting the value, configuraiton of superuser will be used.
