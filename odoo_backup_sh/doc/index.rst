===============
 S3 Backing up
===============

Installation
============

* Install `a Python wrapper for GnuPG <https://pypi.org/project/pretty-bad-protocol>`__ ::

    pip install pretty-bad-protocol

* Install `Amazon Web Services (AWS) SDK for Python <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`__ ::

    pip install boto3

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Database manager
----------------

* To enable the ability to restore databases from your remote backups in a new odoo instance:


  * Add ``odoo_backup_sh`` to `--load parameter <https://odoo-development.readthedocs.io/en/latest/admin/server_wide_modules.html>`__, e.g.::

    ./odoo-bin --workers=2 --load web,odoo_backup_sh --config=/path/to/odoo.conf

  * Use Odoo-backup.sh service (not your personal S3 credentials):

    * Open the menu ``[[ Backups ]] >> Dashboard``
    * Click ``[Get S3 Credentials]``
    * After redireсtion please login in `Odoo.com <https://www.odoo.com/web/login>`__
    * You will be redirected back to the Dashboard with a link to purchase *Credits*. Once it's done, open Backup Dashboard again and click ``[Get S3 Credentials]`` one more time

Personal S3 Storage
-------------------

If you already have S3 bucket with IAM credentials, you can setup your personal S3 storage for backups:

* Open the menu ``[[ Backups ]] >> Settings``
* Set following fields:

  * **S3 Bucket**
  * **Path**, e.g. ``odoo-backups``. Note that the folder must exist
  * **Access Key ID**
  * **Secret Access Key**

Backup Schedule and rotation
----------------------------

To setup backups do as following:

* Open the menu ``[[ Backups ]] >> Dashboard``.
* Click on the ``[Add Database]`` button in the dashboard header.

  * **Database:** select one of your databases
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

* Configure Backup Schedule as described above
* Open the menu ``[[ Backups ]] >> Dashboard``
* Click on ``[Make Backup now]``

RESULT: Backup is created. *Note, that the manual backup creation may take some time before being ready*.


Database manager: restore database
----------------------------------

* Proceed to the Database Manager: ``/web/database/manager``
* Click on ``Restore via Odoo-backup.sh`` button
* Choose the backup that you want to restore
* In the open Pop-up window enter Master Password, fill the Database Name*
* In order to avoid conflicts between databases choose if this database was moved or copied
* Click on ``Continue`` button

RESULT: Backup is restored in one click without any additional manipulations such as "downloading-uploading process".

Downloading backups to computer
-------------------------------

* Be sure that you have **Backup: Manager** access level
* Open ``[[ Backups ]] >> Backups`` menu
* Click on needed Backup from the list
* Click on ``Download`` button and wait until download completes

RESULT: Backup is downloaded.

* If Backup is encrypted (it has `.enc` extension), extract it using `gpg` utility. For example:
  ::
      gpg --output OUTPUT_FILENAME.zip --decrypt INPUT_FILENAME.zip.enc



.. note:: Type the password when it will be prompted


Backup Dashboard
----------------

* Open the menu ``[[ Backups ]] >> Dashboard``

RESULT: You can see the main Graph with the general statistics of all your backups are stored on a remote server.
