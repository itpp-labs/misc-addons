=====================
 Multi-Brand Backend
=====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* As this is a technical module, consider to install other modules that use this one, for example `ir_config_parameter_multi_company <https://apps.odoo.com/apps/modules/13.0/ir_config_parameter_multi_company/>`_

Configuration
=============

Activate **Multi Websites for Backend**:

* Activate `Developer mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Navigate to ``[[ Settings ]] >> Users >> Users`` and set ``[x] Multi Websites for Backend`` for selected users

Usage
=====

Website Switcher
----------------
Once you activated **Multi Websites for Backend**, will see *Website Switcher* in top right-hand corner.

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

On computing in non-website specific context it works as without the module, i.e.:

#. **Company** and **Resource**  are matched
#. **Company** is matched, **Resource** is empty
#. **Company** and **Resource** are empty (i.e. only **Field** is matched)
