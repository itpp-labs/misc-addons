# -*- coding: utf-8 -*-
import logging

from odoo import api
from odoo.tests.common import HttpCase

_logger = logging.getLogger(__name__)


class TestResizedAttachments(HttpCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestResizedAttachments, self).setUp()
        self.original_image_url = 'https://upload.wikimedia.org/wikipedia/commons/1/1e/Gullfoss%2C_an_iconic_waterfall_of_Iceland.jpg'

    def _get_odoo_image_url(self, model, record_id, field):
        return '/web/image?model={}&id={}&field={}'.format(model, record_id, field)

    def test_getting_cached_images_url_instead_computing(self):
        env = api.Environment(self.registry.test_cr, self.uid, {})

        ir_attachment_save_option = env['ir.config_parameter'].get_param('ir_attachment.save_option', default='url')
        if ir_attachment_save_option != 's3':
            _logger.warning('This test only works if "ir_attachment.save_option" = "s3"! '
                            '(ir_attachment.save_option = %s)' % ir_attachment_save_option)
            return

        product_tmpl = env['product.template'].create({
            'name': 'Test template',
            # set the image so that it is not installed from the product (is the white pixel)
            'image': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
        })

        product_product = env['product.product'].create({
            'name': 'Test product',
            'image_variant': self.original_image_url,
            'product_tmpl_id': product_tmpl.id
        })

        odoo_image_url = self._get_odoo_image_url('product.product', product_product.id, 'image')
        odoo_image_medium_url = self._get_odoo_image_url('product.product', product_product.id, 'image_medium')
        odoo_image_small_url = self._get_odoo_image_url('product.product', product_product.id, 'image_small')

        self.authenticate('demo', 'demo')

        redirected_image_url = self.url_open(odoo_image_url, timeout=30).geturl()
        redirected_image_medium_url = self.url_open(odoo_image_medium_url, timeout=30).geturl()
        redirected_image_small_url = self.url_open(odoo_image_small_url, timeout=30).geturl()

        # Attachments must be created during the execution of requests that are written above.
        product_product_image_variant_attachment = env['ir.http']._find_field_attachment(env, 'product.product', 'image_variant', product_product.id)
        product_product_image_attachment = env['ir.http']._find_field_attachment(env, 'product.product', 'image', product_product.id)
        product_product_image_medium_attachment = env['ir.http']._find_field_attachment(env, 'product.product', 'image_medium', product_product.id)
        product_product_image_small_attachment = env['ir.http']._find_field_attachment(env, 'product.product', 'image_small', product_product.id)

        a = set(product_product_image_variant_attachment.resized_ids.mapped('resized_attachment_id'))
        b = {product_product_image_attachment, product_product_image_medium_attachment, product_product_image_small_attachment}
        self.assertFalse(a.difference(b))

        self.assertTrue(product_product_image_attachment)
        self.assertTrue(product_product_image_medium_attachment)
        self.assertTrue(product_product_image_small_attachment)

        self.assertEqual(redirected_image_url, product_product_image_attachment.url)
        self.assertEqual(redirected_image_medium_url, product_product_image_medium_attachment.url)
        self.assertEqual(redirected_image_small_url, product_product_image_small_attachment.url)

        urls = [self.original_image_url, redirected_image_url, redirected_image_medium_url, redirected_image_small_url]
        self.assertEqual(len(urls), len(set(urls)), 'Duplicates in URLs: %s' % urls)

    # TODO
    def test_unlink_resized_attachments_when_parent_unlink(self):
        return
