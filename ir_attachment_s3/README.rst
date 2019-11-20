=======================
 S3 Attachment Storage
=======================

* The module allows to upload the attachments in Amazon S3 automatically without storing them in Odoo database. It will allow to reduce the load on your server. Attachments will be uploaded on S3 depending on the condition you specified in Odoo settings. So you can choose and manage which type of attachments should be uploaded on S3.
* It is useful in cases where your database was crashed, because you will be able to easily restore all attachments from external storage at any time.
* The possibility to use one external storage for any number of databases.

Roadmap
=======

* Create new module `ir_attachment_image` and move following classes, methods from this module to new one:

  * class `BinaryExtended` (excluding s3-related check)
  * class `IrAttachmentResized`
  * partially class `IrAttachment`. Leave s3-related methods here and `_inverse_datas`
  * method `test_getting_cached_images_url_instead_computing`. Probably this modules's test must override test from `ir_attachment_image`

* Refactoring:

  * `S3Setting.upload_existing` and `IrAttachment._inverse_datas` look almost equal

* In settings add options:

  * condition, if object in s3 must be stored as public (as it does now)
  * condition, if object in s3 must be stored as private and think about, how to return it to user, 'cos you cannot use link to that. Possibly read from bucket and return and uncomment this: https://github.com/it-projects-llc/misc-addons/pull/775/files#r302856876

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

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/11.0/ir_attachment_s3/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

HTML Description: https://apps.odoo.com/apps/modules/11.0/ir_attachment_s3/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 11.0 2aeedd044d775c772e811316be301634bcc991b8
