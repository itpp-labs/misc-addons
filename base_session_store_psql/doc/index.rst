==============================
 Store sessions in postgresql
==============================

Installation
============

To use module, add it to ``--load`` parameter. E.g. ::

     ./odoo.py --load=web,web_kanban,base_session_store_psql

In current implementation, you don't need to install module via odoo interface.

It's recommended to `patch <https://github.com/it-projects-llc/install-odoo/blob/11.0/install-odoo-saas.sh#L392-L405>`_ odoo to exclude database from loading list, otherwise it's treated as normal odoo database (with base module installed, cron is running, etc.)

Configuration
=============

You can use ``session_store_db`` parameter in config file (default value is ``session_store``) to specify database where sessions are stored. 


Uninstallation
==============

To uninstall the module delete it from ``--load`` parameter.
