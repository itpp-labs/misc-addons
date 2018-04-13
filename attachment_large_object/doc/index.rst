=========================
 attachment_large_object
=========================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

**Once the module is installed**,
to have ``ir.attachment`` records been stored as large objects by
default, set the following record in ``ir.config_parameter``:

:key: ``ir_attachment.location``
:value: ``postgresql:lobject``

Preexisting attachments are unaffected.

.. warning:: If you do that setting before installing the module
             you will get inconsistent data in ``ir.attachment``
             field ``is_lobject`` will be set to ``True``.

To apply new storage for all existed attachments use module `ir_attachment_force_storage <https://www.odoo.com/apps/modules/11.0/ir_attachment_force_storage/>`_.

Uninstallation
==============

Before uninstallation you need to move all large objects back to default storage type. One of the way to do it is as following:

* install module `ir_attachment_force_storage <https://www.odoo.com/apps/modules/11.0/ir_attachment_force_storage/>`_
* set ``ir_attachment.location`` to **file** or **db**
* now you can safely unistall ``attachment_large_object`` and ``ir_attachment_force_storage``

