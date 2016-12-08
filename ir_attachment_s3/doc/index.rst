=======================
 S3 Attachment Storage
=======================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* `Using this quickstart instruction <https://boto3.readthedocs.io/en/latest/guide/quickstart.html>`__ install boto3 library and get credentials for it
* `Using this instruction <http://mikeferrier.com/2011/10/27/granting-access-to-a-single-s3-bucket-using-amazon-iam>`__ grant access to your s3 bucket
* Optionaly, add following parameter to prevent heavy logs from boto3 library:

    --log-handler=boto3.resources.action:WARNING

Configuration
=============

Instruction how to configure the module.

* `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`__
* Open menu ``Settings >> Parameters >> System Parameters`` and specify the following parameters there

  * ``s3.bucket``: the name of your bucket (e.g. ``mybucket``)
  * ``s3.condition``: only the attachments that meet the condition will be sent to s3 (e.g. ``attachment.res_model == 'product.template'``) - it is actually the way of specifying the models with ``fields.Binary`` fields that should be stored on s3 instead of local file storage or db. Don't specify anything if you want to store all your attachment data from ``fields.Binary`` and also ordinary attachments on s3.
  * ``s3.access_key_id``
  * ``s3.secret_key``

Usage
=====

Depending on what you have in the ``s3.condition`` setting, some or all attachments will be uploaded on your s3.
For example upload by editing product template from ``Sales >> Product`` menu some image for your product.
By doing this you have uploaded image on your s3 storage.
In this case you should also install ``ir_attachment_url`` module to be able to see products' images in odoo backend. Because by default odoo doesn't use urls in its backend. It uses only local stored files or stored db data.
