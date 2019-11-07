====================
 Dropbox backing up
====================

Installation
============

* Install `Dropbox for Python SDK <https://www.dropbox.com/developers/documentation/python#install>`__ ::

    pip install dropbox

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Access Token
------------

Note: You need to have a Dropbox account.

* Open the `App Console <https://www.dropbox.com/developers/apps>`__
* Login/Register into Dropbox account.
* Click on `Create app`

  .. image:: create-app.png

* Choose an API e.g. `Dropbox API`
* Choose the type of access e.g. `App folder`
* Specify the name of your App e.g. `Odoo Backups`
* Read and accept the agreement
* Click on `Create app` button

  .. image:: create-app-form.png

* Click on `Generate` button in order to Generated access token

  .. image:: generate-token.png

* Save the access token

Folder in Dropbox
-----------------

* Open `Dropbox > Apps <https://www.dropbox.com/home/Apps/>`__
* Choose the application you just created
* Create new folder, e.g. *ProductionBackups*

Odoo Settings
---------------

* Open menu ``[[ Backups ]] >> Settings``
* Specify *Dropbox Access Token*
* Specify your folder path, e.g. ``/ProductionBackups``
* Click on ``[Save]`` button

Backup Schedule and rotation
----------------------------

.. this sections is a copy-paste from odoo_backup_sh/doc/index.rst with adding a line about Storage Service

To setup backups do as following:

* Open the menu ``[[ Backups ]] >> Dashboard``.
* Click on the ``[Add Database]`` button in the dashboard header.

  * **Database:** select one of your databases
  * **Storage Service:** select *Dropbox*
  * Encrypt your backup if you need, but do not forget the password
  * Scheduled Auto Backups

    * **Interval**  type an inteval value and select a unit of measure. Example: *make backups every 1 day*.
    * **Next Execution Date:** It shows next planned auto backup date. You can correct this. Example: *make every day at night time*.

  * **Auto Rotation:** If you have set up the auto backup, you can specify how many backups to preserve for certain time frames.

    Example: The module makes auto backup your database every night. You want to preserve 2 daily backups and 1 weekly only. Then

    * *Set up Daily and Weekly rotation options as Limited and put the numbers in limit fields.*

    * *All other options mark as Disabled*.

  * After all required fields will be filled, click on the ``[Save]`` button.

Usage
=====

Manual backups
--------------

.. this sections is a copy-paste from odoo_backup_sh/doc/index.rst

* Configure Backup Schedule as described above
* Open the menu ``[[ Backups ]] >> Dashboard``
* Click on ``[Make Backup now]``

RESULT: Backup is created. *Note, that the manual backup creation may take some time before being ready*

Backup Dashboard
----------------

.. this sections is a copy-paste from odoo_backup_sh/doc/index.rst

* Open the menu ``[[ Backups ]] >> Dashboard``

RESULT: You can see the main Graph with the general statistics of all your backups are stored on a remote server.

Downloading backups to computer
-------------------------------

To download backup (e.g. for restoring in odoo), you can nagivate to dropbox or
download directly in odoo. Note that in later case your browser could show you a
security warning. Just ignore it.
