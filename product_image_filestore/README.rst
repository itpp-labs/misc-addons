This module uses ir.attachment table to handle product images. It
allows store product images on a disk instead of a database.

WARNING
=======

    Installation or deleting this module will cause lost of your
    current product images. Before doing it you have to export images
    from all product variants and then import it back after
    installation or deleting the module.

    During importing images, you can get error "field larger than
    field limit (131072)". At the link below you can find a solution.

    After unintalling this module you also have to update "product"
    module. This cause updating of all dependent modules.

Tested on Odoo 8.0 935141582f5245f7cf5512285d3d91dfe58cb570

Further information and discussion: http://yelizariev.github.io/odoo/module/2015/03/06/product-image-filestore.html
