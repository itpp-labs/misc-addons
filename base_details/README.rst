.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

==============
 Base Details
==============

The module allows to add reference in any models. The reference consist of model name and record id. A list of models is contained in the ``details_model`` field. It's generated in the ``_model_selection`` function which can be overridden in your code. Also the module adds property ``details`` what allows get record with details, e.g.::

    self.product_id.details

Credits
=======

Contributors
------------
* <krotov@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/10.0

HTML Description: https://apps.odoo.com/apps/modules/10.0/base_details/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 11.0 e9454e79e27d0b85546132cbe00b391e974c66bf
