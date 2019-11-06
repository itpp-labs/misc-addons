=========================
 Google Drive backing up
=========================

Installation
============

* Install `Google API Client Library for Python <https://developers.google.com/api-client-library/python/>`__ ::

    pip install google-api-python-client

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Creating a Service Account Key
------------------------------

Note: You need to have a Google account with activated access to `Google Cloud Platform <https://cloud.google.com/>`__.

* `Create new Project <https://console.cloud.google.com/projectcreate>`__ in Google Cloud 
* Switch to the created Project
* Open navigation menu (*Burger menu in the Left corner*), choose ``API & Services >> Library``

  .. image:: api-library-menu.png

* Choose Google Drive API and turn it on

  .. image:: enable-api.png

* Open navigation menu (*Burger menu in the Left corner*), choose ``IAM & admin >> Service accounts``

  .. image:: service-accounts-menu.png

* Click on ``+ CREATE SERVICE ACCOUNT``

  * Set name, e.g. ``Odoo Backups`` and click ``[Create]`
  * At next the step set permission ``Project >> Owner``

    .. image:: service-account-permission.png

  * At the last stage click ``+ CREATE KEY``

    * Use key type ``JSON``

      .. image:: create-key.png

  * A json file is downloaded. You will need it later


Access rights to Google Folder
------------------------------

* Go to `Google Drive <https://www.google.com/drive/>`__
* Create a new folder, say `Odoo Backups`
* Open folder and click `Share` button in folder menu

  .. image:: share-button.png

* In Pop up window fill in e-mail of created service account. It should have Edit access

  * You can find service account e-mail in Google Cloud in menu ``IAM & admin >> Service accounts``

* Confirm your action

  .. image:: share-folder.png

* Check URL in your browser. It has following format:
  ``https://drive.google.com/drive/folders/1oRL3sEKsk9i9Iripu7hsroaYpefl4DO4``,
  where last part is the *Folder ID*: ``1oRL3sEKsk9i9Iripu7hsroaYpefl4DO4``. You will need it later.

  .. image:: folder-id.png

Odoo Settings
---------------

* Open menu ``[[ Backups ]] >> Settings``
* Paste content of the Key file into *Service Account Key* field
* Paste *Folder ID* value into *Google Drive Folder ID*
* Click on ``[Save]`` button

Backup Schedule and rotation
----------------------------

.. this sections is a copy-paste from odoo_backup_sh/doc/index.rst with adding a line about Storage Service

To setup backups do as following:

* Open the menu ``[[ Backups ]] >> Dashboard``.
* Click on the ``[Add Database]`` button in the dashboard header.

  * **Database:** select one of your databases
  * **Storage Service:** select *Google Drive*
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
