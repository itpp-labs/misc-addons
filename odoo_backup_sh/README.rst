.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: MIT

===============
 S3 Backing up
===============

Backing up Odoo databases to S3 bucket. 

In-App Purchase
===============

IAP IS TEMPORARLY DISABLED.

**odoo-backup.sh** provides s3 credentials. Payments for the service is managed by proprietary module, which implements `In-App Purchase <https://www.odoo.com/documentation/13.0/webservices/iap.html>`__ -- payments platform provided by *Odoo S.A.*.

Personal cloud
==============

Additionally to the cloud provided by **odoo-backup.sh** it's possible to store backups on a personal cloud. In that case user has to arrange credentials himself. Supported cloud providers and protocols are as following:

* `Dropbox <https://apps.odoo.com/apps/modules/13.0/odoo_backup_sh_dropbox/>`_
* `Google Drive <https://apps.odoo.com/apps/modules/13.0/odoo_backup_sh_google_disk/>`_

*You need to get corresponding modules to use personal cloud.*

Implementation details
======================

/web/database/backups
---------------------

It's a new page in *database manager*, that allows to see list of available backups that can be restored. It works **only** with S3 bucket provided by **odoo-backup.sh service**.

The page is available via new button ``[Restore via Odoo-backup.sh]`` at *database manager*. It works in the following way:

* If there are no amazon S3 credentials in the session, the module makes requests to get them:

  * *Browser* sends request to ``/web/database/backups``
  * *Odoo instance* sends request to ``odoo-backup.sh/get_cloud_params`` with ``user_key`` from the session (the ``user_key`` is generated automatically if it's not set).
  * ``odoo-backup.sh`` **either** returns amazon S3 credentials with which the module can use to send request to S3 independently, **or** ``odoo-backup.sh`` doesn't recognise ``user_key`` and starts process of authentication via ``odoo.com`` as auth provider:

    * ``odoo-backup.sh/get_cloud_params`` returns a link to redirect to odoo.com authentication page
    * *User* enters his login-password and is redirected back to ``/web/database/backups`` page and the process starts again, but this time ``odoo-backup.sh`` recognise ``user_key`` and return amazon credentials

* If amazon S3 credentials are in the config file, the module makes request to AWS S3 to get list of users backups and then renders it.

Backup dashboard
----------------

It's a backend page where an user can watch detail information about his backups
which are remote stored. Also he can make backup of any of his databases. This
backup will be sent to AWS S3 for storing. Moreover the user can create
autobackup settings. The settings say to the module at what point of time, from
which databases to create backups and max number of backups of database must be
store. Backups rotations are supported too.

After module installation user can click ``Get S3 credentials``, which start similar process are described above in ``/web/database/backups`` section.

Manual Testing
==============

To test odoo_backup_sh* modules one can use following scenarios:

Test: rotation
--------------

* Use database with demo
* Install ``odoo_backup_sh``
* Open menu ``[[ Backups ]]``
* Click ``[Get S3 storage]``
* At demo Backup Config set any backup schedule
* Configure rotation to test
* Go to ``[[ Settings ]] >> Automation >> Scheduled Actions``

  * Find a cron job for backuping and click ``[Run Manually]``

* Check that backups are rotated according to plan
* To repeat the test open Backup Config and click ``[Create Fake Backups]``

Preparation: Install base module
--------------------------------

* use database without demo
* if you previously installed backup modules, then uninstall them and delete ``odoo_backup_sh.*`` params in ``[[ Settings ]] >> System Parameters``. 
* install ``odoo_backup_sh``


Test: IAP S3
------------


* Install base module
* Click ``[Get S3 storage]``
* Create Schedule for current database. Test from this step should be proceeded in two different scenarios: with encryption disabled and enabled
* Test according to *Checklist: Backups*

Restoring without downloading:

* In new incognito window open ``/web/database/manager``
* In ``Odoo-backup.sh`` section restore database
* Login to the restored database -- all scheduled backuping must be disabled

Test: S3
--------

* Install base module
* Configure private S3 credentials according to the instruction
* Create Schedule for current database.
* Test according to *Checklist: Backups*

Checklist: Backups
------------------

* Directly at the storage: create manually some file to check that modules can handle them:

  * a file with random name
  * a backup without corresponding ``*.info`` file
  * a backup info file without backup itself

* Go to ``[[ Settings ]] >> Automation >> Scheduled Actions``

  * Find a cron job for backuping and click ``[Run Manually]``

* Go to ``[[ Settings ]] >> Backups``

  * Find just created backup
  * Click ``[Download]``
  * If database is encrypted, decrypt it as described in  `<doc/index.rst>`__
  * Restore database in a usual way

Manual backups:

* Go to Dashboard
* Click ``[Make backup now]``
* Download the backup again as described above

Syncing with remote backups:

* Directly at the storage:

  * copy archive for a backup and set new name (e.g. change year of the backup)
  * copy info file of the backup and make corresponing name in its name and content

* Go to ``[[ Settings ]] >> Automation >> Scheduled Actions``

  * Find a cron job for backuping and click ``[Run Manually]``

* Go to ``[[ Settings ]] >> Backups``

  * Check that copied backup has a record in Backup list. If there is no one, be
    sure that the Backup Settings doesn't have rotations.
  * Download the backup


Test: Dropbox only
------------------
* *Install base module*
* Install ``odoo_backup_sh_dropbox`` module
* Configure dropbox according to the module's documentation
* Create Schedule for any database
* Test according to *Checklist: Backups*

Test: All storages
------------------
* *Install base module*
* Install ``odoo_backup_sh_dropbox`` module
* Install ``odoo_backup_sh_google_disk`` module
* Configure S3 only credentials, Create Schedule
* Test according to *Checklist: Backups*
* Configure Dropbox credentials, Create Schedule
* Test according to *Checklist: Backups*
* Configure Google Drive credentials, Create Schedule
* Test according to *Checklist: Backups*

Test: IAP Notification
----------------------

TODO

Test: IAP Credits
-----------------

TODO: Check purchasing, top-up, using credits, running out of credits

Roadmap
=======

* All backups modules should be refactored and cleaned up.

  * See TODOs in code
  * odoo_backup_sh.py files should splitted according to odoo guidelines

* non-active records in config_cron_ids should be visible. But visibility of warning and rotation fields should depend on active crons only

Credits
=======

Contributors
------------
* `Stanislav Krotov <https://it-projects.info/team/ufaks>`__
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/13.0/odoo_backup_sh/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/13.0

HTML Description: https://apps.odoo.com/apps/modules/13.0/odoo_backup_sh/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 12.0 483b6024cd44fcc6e2b987505beb739014b51856
