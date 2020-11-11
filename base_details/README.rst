.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

==============
 Base Details
==============

The module allows to add reference in any models. The reference consist of model name and record id. A list of models is contained in the ``details_model`` field. It's generated in the ``_model_selection`` function which can be overridden in your code. Also the module adds property ``details`` what allows get record with details, e.g.::

    self.product_id.details

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* <krotov@it-projects.info>



Tested on `Odoo 11.0 <https://github.com/odoo/odoo/commit/e9454e79e27d0b85546132cbe00b391e974c66bf>`_
