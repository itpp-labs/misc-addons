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

You can ``session_store_db`` value in config file (default value is ``session_store``). This database will be used to store sessions. 


Uninstallation
==============

To uninstall the module delete it from ``--load`` parameter.
