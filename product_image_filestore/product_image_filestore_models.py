# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, tools

import logging
import sys

_logger = logging.getLogger(__name__)


class ProductTemplate(osv.Model):
    _inherit = "product.template"

    def _auto_init(self, cr, context=None):
        # Check that we have an image column
        cr.execute("select COUNT(*) from information_schema.columns where table_name='product_template' AND column_name='image';")
        res = cr.dictfetchone()
        if res.get('count'):
            _logger.info('Starting conversion for product_template: saving data for further processing.')
            # Rename image column so we don't lose images upon module install
            cr.execute("ALTER TABLE product_template RENAME COLUMN image TO image_old")
            cr.commit()
        else:
            _logger.info('No image field found in product_template; no data to save.')
        return super(ProductTemplate, self)._auto_init(cr, context=context)

    def _auto_end(self, cr, context=None):
        super(ProductTemplate, self)._auto_end(cr, context=context)
        # Only proceed if we have the appropriate _old field
        cr.execute("select COUNT(*) from information_schema.columns where table_name='product_template' AND column_name='image_old';")
        res = cr.dictfetchone()
        if res.get('count'):
            _logger.info('Starting rewrite of product_template, saving images to filestore.')
            errors_encountered = False
            # Rewrite all records to store the images on the filestore
            for template_id in self.pool.get('product.template').search(cr, SUPERUSER_ID, [], context=context):
                wvals = {}
                cr.execute("SELECT image_old FROM product_template WHERE id = %s", (template_id, ))
                res = cr.dictfetchone()
                datas = res.get('image_old')
                if datas:
                    wvals.update({'image': datas[:]})
                    try:
                        self.pool.get('product.template').write(cr, SUPERUSER_ID, template_id, wvals)
                        cr.execute("UPDATE product_template SET image_old = null WHERE id=%s", (template_id, ))
                    except:
                        errors_encountered = True
                        filename = '/tmp/product_template_image_%d.b64' % (template_id, )
                        with open(filename, 'wb') as f:
                            f.write(datas)
                        _logger.error('Failed to convert image for product template %d - raw base-64 encoded data stored in %s' % (template_id, filename))
                        _logger.error('The error was: %s' % sys.exc_info()[0])
            # Finally, remove the _old column if all went well so we won't run this every time we upgrade the module.
            # If we encountered errors, or there's still data left in image_old, rename instead and log an error. Fixes #265
            cr.execute("SELECT COUNT(*) FROM product_template WHERE image_old IS NOT NULL AND image_old != ''")
            if errors_encountered or res.get('count'):
                cr.execute("ALTER TABLE product_template RENAME COLUMN image_old TO image_bkp")
                _logger.error('Failed to convert all images in product_template. Data left intact in column image_old, manual intervention required.')
            else:
                cr.execute("ALTER TABLE product_template DROP COLUMN image_old")
            cr.commit()
        else:
            _logger.info('No image_old field present in product_template; assuming data is already saved in the filestore.')

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'image': obj.image_attachment_id and obj.image_attachment_id.datas or None,
                'image_small': obj.image_small_attachment_id and obj.image_small_attachment_id.datas or None,
                'image_medium': obj.image_medium_attachment_id and obj.image_medium_attachment_id.datas or None,
            }
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        obj = self.browse(cr, uid, id, context=context)
        image_id = obj.image_attachment_id.id
        image_small_id = obj.image_small_attachment_id.id
        image_medium_id = obj.image_medium_attachment_id.id
        if not value:
            ids = [attach_id for attach_id in [image_id, image_small_id, image_medium_id] if attach_id]
            if ids:
                self.pool['ir.attachment'].unlink(cr, uid, ids, context=context)
            return True
        if not (image_id and image_small_id and image_medium_id):
            image_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Product Image'}, context=context)
            image_small_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Product Small Image'}, context=context)
            image_medium_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Product Medium Image'}, context=context)
            self.write(cr, uid, id, {'image_attachment_id': image_id,
                                     'image_small_attachment_id': image_small_id,
                                     'image_medium_attachment_id': image_medium_id},
                       context=context)

        images = tools.image_get_resized_images(value, return_big=True, avoid_resize_medium=True)
        self.pool['ir.attachment'].write(cr, uid, image_id, {'datas': images['image']}, context=context)
        self.pool['ir.attachment'].write(cr, uid, image_small_id, {'datas': images['image_small']}, context=context)
        self.pool['ir.attachment'].write(cr, uid, image_medium_id, {'datas': images['image_medium']}, context=context)

        return True

    _columns = {
        'image_attachment_id': fields.many2one('ir.attachment', 'Image attachment', help='Technical field to store image in filestore'),
        'image_small_attachment_id': fields.many2one('ir.attachment', 'Small-sized Image  attachment', help='Technical field to store image in filestore'),
        'image_medium_attachment_id': fields.many2one('ir.attachment', 'Medium-sized Image  attachment', help='Technical field to store image in filestore'),

        'image': fields.function(_get_image, fnct_inv=_set_image, string="Image", multi='_get_image', type='binary',
                                 help="This field holds the image used as image for the product, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        help="Medium-sized image of the product. It is automatically "
                                        "resized as a 128x128px image, with aspect ratio preserved, "
                                        "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       help="Small-sized image of the product. It is automatically "
                                       "resized as a 64x64px image, with aspect ratio preserved. "
                                       "Use this field anywhere a small image is required."),
    }


class ProductProduct(osv.Model):
    _inherit = "product.product"

    def _auto_init(self, cr, context=None):
        # Check that we have an image_variant column
        cr.execute("select COUNT(*) from information_schema.columns where table_name='product_product' AND column_name='image_variant';")
        res = cr.dictfetchone()
        if res.get('count'):
            _logger.info('Starting conversion for product_product: saving data for further processing.')
            # Rename image column so we don't lose images upon module install
            cr.execute("ALTER TABLE product_product RENAME COLUMN image_variant TO image_variant_old")
            cr.commit()
        else:
            _logger.info('No image_variant field found in product_product; no data to save.')
        return super(ProductProduct, self)._auto_init(cr, context=context)

    def _auto_end(self, cr, context=None):
        super(ProductProduct, self)._auto_end(cr, context=context)
        # Only proceed if we have the appropriate _old field
        cr.execute("select COUNT(*) from information_schema.columns where table_name='product_product' AND column_name='image_variant_old';")
        res = cr.dictfetchone()
        if res.get('count'):
            _logger.info('Starting rewrite of product_product, saving images to filestore.')
            errors_encountered = False
            # Rewrite all records to store the images on the filestore
            for product_id in self.pool.get('product.product').search(cr, SUPERUSER_ID, [], context=context):
                wvals = {}
                cr.execute("SELECT image_variant_old FROM product_product WHERE id = %s", (product_id, ))
                res = cr.dictfetchone()
                datas = res.get('image_variant_old')
                if datas:
                    wvals.update({'image_variant': datas[:]})
                    try:
                        self.pool.get('product.product').write(cr, SUPERUSER_ID, product_id, wvals)
                        cr.execute("UPDATE product_product SET image_variant_old = null WHERE id=%s", (product_id, ))
                    except:
                        errors_encountered = True
                        filename = '/tmp/product_product_image_%d.b64' % (product_id, )
                        with open(filename, 'wb') as f:
                            f.write(datas)
                        _logger.error('Failed to convert image for product variant %d - raw base-64 encoded data stored in %s' % (product_id, filename))
                        _logger.error('The error was: %s' % sys.exc_info()[0])
            # Finally, remove the _old column if all went well so we won't run this every time we upgrade the module.
            # If we encountered errors, or there's still data left in image_variant_old, rename instead and log an error. Fixes #265
            cr.execute("SELECT COUNT(*) FROM product_product WHERE image_variant_old IS NOT NULL AND image_variant_old != ''")
            if errors_encountered or res.get('count'):
                cr.execute("ALTER TABLE product_product RENAME COLUMN image_variant_old TO image_variant_bkp")
                _logger.error('Failed to convert all images in product_product. Data left intact in column image_variant_old, manual intervention required.')
            else:
                cr.execute("ALTER TABLE product_product DROP COLUMN image_variant_old")
            cr.commit()
        else:
            _logger.info('No image_variant_old field present in product_product; assuming data is already saved in the filestore.')

    def _get_image_variant(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        if name == 'image_variant':
            name = 'image'
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image_variant_attachment_id.datas or getattr(obj.product_tmpl_id, name)
        return result

    def _set_image_variant(self, cr, uid, id, name, value, args, context=None):
        obj = self.browse(cr, uid, id, context=context)
        image_variant_id = obj.image_variant_attachment_id.id

        if not value:
            ids = [id for _id in [image_variant_id] if _id]
            if ids:
                self.pool['ir.attachment'].unlink(cr, uid, ids, context=context)
            return True

        if not image_variant_id:
            image_variant_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Product Variant Image'}, context=context)
            self.write(cr, uid, id, {'image_variant_attachment_id': image_variant_id}, context=context)

        image = tools.image_resize_image_big(value)

        product = self.browse(cr, uid, id, context=context)

        res = self.pool['ir.attachment'].write(cr, uid, image_variant_id, {'datas': image}, context=context)

        if not product.product_tmpl_id.image:

            product.image_variant_attachment_id.unlink()
            product.product_tmpl_id.write({'image': image})
        return res

    _columns = {
        'image_variant_attachment_id': fields.many2one('ir.attachment', 'Image Variant attachment', help='Technical field to store image in filestore'),

        'image_variant': fields.function(_get_image_variant, fnct_inv=_set_image_variant, string="Variant Image", type='binary',
                                         help="This field holds the image used as image for the product variant, limited to 1024x1024px."),
        'image': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
                                 string="Big-sized image", type="binary",
                                 help="Image of the product variant (Big-sized image of product template if false). It is automatically "
                                 "resized as a 1024x1024px image, with aspect ratio preserved."),
        'image_small': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
                                       string="Small-sized image", type="binary",
                                       help="Image of the product variant (Small-sized image of product template if false)."),
        'image_medium': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
                                        string="Medium-sized image", type="binary",
                                        help="Image of the product variant (Medium-sized image of product template if false)."),
    }
