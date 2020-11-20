.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

=========================
 Multi System Parameters
=========================

Adds multi-company and multi-website support to many features

Based on built-in ``company_dependent`` and new ``website_dependent`` attributes. Real values are stored at ``ir.property``.

Check Usage instructions for understanding how it works.

Running auto-tests
==================

On following conditions:

* ``at_install`` tests are run in other modules
* during tests ``ir.config_parameter`` is used
* ``ir_config_parameter_multi_company`` is installed, but not loaded yet

The following error may appear::

    ERROR: column ir_config_parameter.value does not exist

To avoid it, add the module to ``--load`` parameter, e.g.::

    ./odoo-bin --load=web,ir_config_parameter_multi_company --test-enable -i some_module ...

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__


Further information
===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/13.0/ir_config_parameter_multi_company/


Tested on `Odoo 13.0 <https://github.com/odoo/odoo/commit/80cef9e8c52ff7dc0715a7478a2288d3de7065df>`_
