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

Credits
=======

Contributors
------------

* `AnyBox <anybox.fr>`__
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__


Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/9.0

.. HTML Description: https://apps.odoo.com/apps/modules/9.0/attachment_large_object/

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 9.0 ce038f5d1531107a1e45fd867de42e82940babdb
