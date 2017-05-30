=======================
 S3 Attachment Storage
=======================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* `Using this quickstart instruction <https://boto3.readthedocs.io/en/latest/guide/quickstart.html>`__ install boto3 library and get credentials for it
* `Using this instruction <http://mikeferrier.com/2011/10/27/granting-access-to-a-single-s3-bucket-using-amazon-iam>`__ grant access to your s3 bucket
* Set your S3 bucket as public
* Optionaly, add following parameter to prevent heavy logs from boto3 library:

    --log-handler=boto3.resources.action:WARNING

Configuration
=============

* To enable the feature of linking existing urls to binary fields:

  * Start Odoo with ``--load=web,ir_attachment_url``
    or set the ``server_wide_modules``
    option in The Odoo configuration file:

::

  [options]
  # (...)
  server_wide_modules = web,ir_attachment_url
  # (...)

* `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`__
* Open menu ``Settings >> Parameters >> System Parameters`` and specify the following parameters there

  * ``s3.bucket``: the name of your bucket (e.g. ``mybucket``)
  * ``s3.condition``: only the attachments that meet the condition will be sent to s3 (e.g. ``attachment.res_model == 'product.template'``) - it is actually the way of specifying the models with ``fields.Binary`` fields that should be stored on s3 instead of local file storage or db. Don't specify anything if you want to store all your attachment data from ``fields.Binary`` and also ordinary attachments on s3.
  * ``s3.access_key_id``: S3 access key ID
  * ``s3.secret_key``: S3 secret access key

The settings are also available from the ``Settings >> Technical >> Database Structure >> S3 Settings``.

Usage
=====

Depending on what you have in the ``s3.condition`` setting, some or all attachments will be uploaded on your s3.
For example upload by editing product template from ``Sales >> Product`` menu some image for your product.
By doing this you have uploaded image on your s3 storage.
In this case you should also install ``ir_attachment_url`` module to be able to see products' images in odoo backend. Because by default odoo doesn't use urls in its backend. It uses only local stored files or stored db data.

* To upload existing attachments go to the ``Settings >> Technical >> Database Structure >> S3 Settings`` menu and click the ``[Upload existing attachments]`` button there
* To add link of existing S3 bucket object to binary fields of existing odoo records:

  * Take ``Link`` urls from Amazon. If you open ``Overview`` of the object on Amazon you should see it at the bottom of the page

  * make sure that you have properly configured your odoo, see the ``Configuration`` section of this instruction once again in the ``To enable feature of linking...`` part

  * to link objects one-by-one from an odoo backend (this option is only abailable for images attachments):

    * In any place where you can upload images to odoo (i.e. from ``Sales >> Sales >> Products`` when you select a product and push ``[Edit]`` button there
      and hove your mouse pointer under the place on a form view where an image should be)
      along with standard pencil and trash bin buttons you can see the additional ``[@]`` button. Click this button.
    * Copy-paste your url for image and click ``[Save]`` button

  * to link objects in batch you may use default import/export feature of odoo:

    * export records, for example of model ``product.template``. Choose ``image`` field in the export dialog and save in file.
    * open the file with your favourite text editor and paste urls into ``image`` column there
    * import records from the edited CSV file
    * now when you open from ``Sales >> Sales >> Products`` your product form you shoud see the image you specify by url in the file
