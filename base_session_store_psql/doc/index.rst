==============================
 Store sessions in postgresql
==============================

Installation
============

To use module add it to ``server_wide_modules`` in config file or run odoo with ``--load`` parameter. E.g. ::

     ./odoo.py --load=web,base_session_store_psql

In current implementation, you don't need to install module.

Usage
=====

Specify ``log_db`` value in config file or run odoo with ``--log-db`` parameter. This database will be used to store sessions.


Uninstallation
==============

To uninstall the module delete it from ``server_wide_modules`` setting.
