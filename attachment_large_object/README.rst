.. advanced_attachment documentation master file, created by
   sphinx-quickstart on Tue Mar 25 19:10:44 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

advanced_attachment addons for OpenERP 7.0
==========================================

These addons enhance OpenERP's native attachment system with several
interesting features.

.. toctree::
   :maxdepth: 2

attachment_large_object
~~~~~~~~~~~~~~~~~~~~~~~

This module provides the option to store attachments as PostgreSQL
large objects.

For general information on the three classical ways to store file-like
content in a PostgreSQL DB, see `this wiki page
<https://wiki.postgresql.org/wiki/BinaryFilesInDB>`_.

OpenERP's default in-database storage is a base64 encoded text column.
The framework also provides a file system storage (tree of directories
so that it scales well on linked lists based file systems such as EXT4)

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
----------
Once the module is installed,
to have ``ir_attachment`` records been stored as large objects by
default, set the following record in ``ir.config_parameter``:

:key: ``ir_attachment.location``
:value: ``postgresql:lobject``

Preexisting attachments are unaffected.

.. note :: for various compatibility reasons, this implementation still does
           the same on-the-fly base64 encoding and decoding as the
           filesystem storage, which is obviously non optimal,
           especially for very large files (over 100 MB).

           At least this puts the strain on the
           application part, not on the database system.
           A later version might bring more options.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

