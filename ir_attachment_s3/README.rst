=======================
 S3 Attachment Storage
=======================

* The module allows to upload the attachments in Amazon S3 automatically without storing them in Odoo database. It will allow to reduce the load on your server. Attachments will be uploaded on S3 depending on the condition you specified in Odoo settings. So you can choose and manage which type of attachments should be uploaded on S3.
* It is useful in cases where your database was crashed, because you will be able to easily restore all attachments from external storage at any time.
* The possibility to use one external storage for any number of databases.

Credits
=======

Contributors
------------
* `Ildar Nasyrov <https://it-projects.info/team/iledarn>`
* `Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>`
* `Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>`
* `Eugene Molotov <https://it-projects.info/team/em230418>`

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`_

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/10.0/ir_attachment_s3/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

HTML Description: https://apps.odoo.com/apps/modules/10.0/ir_attachment_s3/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 10.0 98a137e4b1f631a10d46b5e0cb21bb83ed7e861f
