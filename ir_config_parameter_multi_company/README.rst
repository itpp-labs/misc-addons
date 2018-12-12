===============================================
 Context-dependent values in System Parameters
===============================================

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

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/12.0

HTML Description: https://apps.odoo.com/apps/modules/12.0/ir_config_parameter_multi_company/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 12.0 80cef9e8c52ff7dc0715a7478a2288d3de7065df
