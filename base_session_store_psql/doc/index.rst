==============================
 Store sessions in postgresql
==============================

Installation
============

To use module, add it to ``--load`` parameter. E.g. ::

     ./odoo.py --load=web,web_kanban,base_session_store_psql

In current implementation, you don't need to install module via odoo interface.

Configuration
=============

You can use ``session_store_db`` parameter in config file (default value is ``session_store``) to specify database where sessions are stored. 


Uninstallation
==============

To uninstall the module delete it from ``--load`` parameter.
