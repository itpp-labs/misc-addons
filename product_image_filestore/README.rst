Store product images in filestore
=================================

This module stores the product images in the filestore instead of the database.
It achieves this by storing them as attachments, rather than binary fields on
the Product / Product Variant models.

WARNING
=======

Regular Installation:
---------------------

    Before installing this module, perform a backup of your database,
    and preferably your filestore. Alternatively, instead of backing up
    your filestore, create a listing of the files it contains. That way
    you can remove the newly created files in case you wish to perform
    a rollback.

    During installation, the images are migrated from the DB to the
    filestore, through direct database intervention. This is an invasive
    procecure and not entirely without risk. Therefore, having a rollback
    procedure in place as described above is highly recommended.

    If errors are encountered during installation, an error is logged and
    the contents of the image field in the offending product or variant is
    saved to /tmp/product_template_image_${id}.b64 or
    /tmp/product_product_${id}.b64 for inspection. These files contain the raw
    field data, which under normal circumstances should contain the base64
    encoded contents of the image file, but in some cases may contain
    invalid data such as the string "[False]". If this is the case, those files
    may be safely deleted as they would never have decoded to a valid image
    anyway. When the upgrade fails, the original column containing the data
    that wasn't converted is also preserved, with a '_bkp' suffix, to aid
    with the investigation.

Post-Install:
-------------

    If all goes well, the process is transparent and no further action is
    required. The images are moved from the database to the filestore, and
    the database columns are dropped.

    If the upgrade fails, however, the original fields remain in the database
    but are renamed to the same name with the "_bkp" suffix. For successfully
    converted records, the contents are set to null; for failed conversions,
    the original data remains in the field. This data is the same data that's
    also written to the files in /tmp.

    The files in /tmp are the most convenient way to retrieve all information
    pertaining failed conversions. Since this folder is emptied upon reboot,
    a secondary backup is left in the database in the form of the image_bkp and
    image_variant_bkp columns in product_template and product_product. After
    concluding the investigation into the failure, these columns can be safely
    dropped via following commands:::

        ALTER TABLE product_template DROP COLUMN image_bkp;
        ALTER TABLE product_product  DROP COLUMN image_variant_bkp;


Export/Import:
--------------

    The previous way of retaining your product images is still supported:
    prior to installing this module, export all images from all products
    and product variants, and after installing (or removing) the module,
    re-import them. This should not be necessary as the module now takes
    care of this during installation, but it's still supported.

    While importing images, you can encounter the error "field larger than
    field limit (131072)". A solution for this error can be found at the
    link below.

Deinstalling:
-------------

    After deinstalling this module you also have to update the "product"
    module. This causes an update of all dependent modules. This operation
    is destructive in the sense that it will remove all product images.
    If you wish to retain them, see Export/Import above.

Tested on Odoo 8.0 935141582f5245f7cf5512285d3d91dfe58cb570 and
d24ff706a9194fe33c9f98aca0c0424486b661cf

Further information and discussion: http://yelizariev.github.io/odoo/module/2015/03/06/product-image-filestore.html

9.0+
====

The module is obsolete in 9.0 and later versions, because `odoo 9.0+ stores images on filestore by default <http://stackoverflow.com/questions/36620976/where-does-odoo-9-physically-store-the-image-field-of-res-partner-records-in/36622134?stw=2#36622134>`__ 

Credits
=======

Author:
-------
    * Ivan Yelizariev, IT-Projects LLC, https://github.com/yelizariev

Contributors:
-------------
    * Juan Rial, https://github.com/jrial
