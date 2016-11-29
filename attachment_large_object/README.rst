.. advanced_attachment documentation master file, created by
   sphinx-quickstart on Tue Mar 25 19:10:44 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

advanced_attachment addons for OpenERP 8.0
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
**Once the module is installed**,
to have ``ir_attachment`` records been stored as large objects by
default, set the following record in ``ir.config_parameter``:

:key: ``ir_attachment.location``
:value: ``postgresql:lobject``

Preexisting attachments are unaffected.

.. warning:: If you do that setting before installing the module
             you will get inconsistent data in ``ir.attachment``
             field ``is_lobject`` will be set to ``True``.

.. note :: for various compatibility reasons, this implementation still does
           the same on-the-fly base64 encoding and decoding as the
           filesystem storage, which is obviously non optimal,
           especially for very large files (over 100 MB).

           At least this puts the strain on the
           application part, not on the database system.
           A later version might bring more options.

Data recovery procedure
-----------------------

To transfer your data from *file system* or from *base64 encoded text column*
to *large object* you can use the ``convert_attachment`` script.

This will basicly read the attachment and save it as ``lobject``.

Install from buildout
~~~~~~~~~~~~~~~~~~~~~

Here a basic config to install script in your environment using buildout,
``buildout.cfg`` file looks like::

    [buildout]
    parts = odoo
    versions = versions
    find-links = http://download.gna.org/pychart/
    extensions = gp.vcsdevelop
    vcs-extend-develop = hg+https://bitbucket.org/anybox/advanced_attachment@8.0#egg=advanced.attachment.scripts

    [odoo]
    recipe = anybox.recipe.odoo:server
    version = git https://github.com/OCA/OCB.git ocb 8.0
    addons = hg https://bitbucket.org/anybox/advanced_attachment community-addons/advanced_attachment 8.0

    openerp_scripts = convert_attachment=convert_attachment arguments=session

    eggs =
        PyPDF
        advanced.attachment.scripts

    [versions]
    ...


Usage
~~~~~
Assuming you install this script with the upper buildout config::

    bin/convert_attachment --help
    usage: convert_attachment [-h] [-d DATABASE] [-N TRANSACTION_NUMBER]
                              [-F MAX_FILE_SIZE] [-p ODOO_DATA_DIR] [-s] [-f]

    Script to upgrade odoo attachment to large object attachment.

    optional arguments:
      -h, --help            show this help message and exit
      -d DATABASE, --database DATABASE
                            Database to work on
      -N TRANSACTION_NUMBER, --transaction-number TRANSACTION_NUMBER
                            Tell how often commit. Default, commit every 50
                            attachments
      -F MAX_FILE_SIZE, --max-file-size MAX_FILE_SIZE
                            Max file size to upgrade (in octets)
      -p ODOO_DATA_DIR, --odoo-data-dir ODOO_DATA_DIR
                            Odoo filestore directory, default
                            /home/you/.local/share/Odoo.
      -s, --simulate        Simulation mode: just logs actions but does not
                            perform.
      -f, --force           Do not raise if attachment data is missing,carry on
                            silently

``-F`` and ``-N`` options are there to let you manage memory usage when
transfer data to avoid memory error.

.. note:: the simulate mode does not perform any database write (it's
          not only doing rollbacks), because that would actually remove the
          file from disk. You can't have a reliable estimation of
          execution time through it.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

