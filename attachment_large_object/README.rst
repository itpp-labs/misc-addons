=========================
 attachment_large_object
=========================

Provides a storage option for attachments as PostgreSQL large objects.

For general information on the three classical ways to store file-like
content in a PostgreSQL DB, see `this wiki page
<https://wiki.postgresql.org/wiki/BinaryFilesInDB>`_.

Also, check authors' blog post: https://anybox.fr/blog/postgresql-large-object-storage-for-odoo

Advantages
==========

Odoo supports two types of storage:

* in-database storage is a base64 encoded text column.
* file system storage (tree of directories so that it scales well on linked lists based file systems such as EXT4)

Advantages over the default in-database storage
-----------------------------------------------
- better RAM efficiency (the bigger each individual file is, the more
  this is true)
- possibility to dump easily the base without the large objects (very useful
  for bug reproduction)

Advantages over the file system storage
----------------------------------------
Nothing can beat the file system in terms of read/write
performance. That being said, large objects

- are transactional (fully ACID)
- work out of the box in multi-system setups (no need for NFS or
  similar file sharing tools)
- keep allowing easy, consistent backups of the whole system

How to use
==========
**Once the module is installed**,
to have ``ir_attachment`` records been stored as large objects by
default, set the following record in ``ir.config_parameter``:

:key: ``ir_attachment.location``
:value: ``postgresql:lobject``

Preexisting attachments are unaffected.

.. warning:: If you do that setting before installing the module
             you will get inconsistent data in ``ir.attachment``
             field ``is_lobject`` will be set to ``True``.

To apply new storage for all existed attachments use module `ir_attachment_force_storage <https://www.odoo.com/apps/modules/10.0/ir_attachment_force_storage/>`_.

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/8.0

HTML Description: https://apps.odoo.com/apps/modules/8.0/attachment_large_object/

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 8.0 8d724924f76a943035a8aa2d1b446418fd6b4034
