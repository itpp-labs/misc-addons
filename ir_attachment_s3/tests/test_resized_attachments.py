# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).
import logging

from odoo import api, exceptions
from odoo.tests.common import HttpCase, tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestResizedAttachments(HttpCase):
    def setUp(self):
        super(TestResizedAttachments, self).setUp()
        self.original_image_url = "https://upload.wikimedia.org/wikipedia/commons/1/1e/Gullfoss%2C_an_iconic_waterfall_of_Iceland.jpg"

    def _get_odoo_image_url(self, model, record_id, field):
        return "/web/image?model={}&id={}&field={}".format(model, record_id, field)

    def test_getting_cached_images_url_instead_computing(self):
        env = api.Environment(self.registry.test_cr, self.uid, {})

        env["ir.config_parameter"].set_param("ir_attachment_url.storage", "s3")

        if not env["ir.attachment"]._get_s3_resource():
            self.skipTest("Bad S3 credidentials given")
            return

        product_tmpl = env["product.template"].create(
            {
                "name": "Test template",
                # set the image so that it is not installed from the product (is the white pixel)
                "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            }
        )

        product_product = env["product.product"].create(
            {
                "name": "Test product",
                "image_variant": self.original_image_url,
                "product_tmpl_id": product_tmpl.id,
            }
        )

        odoo_image_url = self._get_odoo_image_url(
            "product.product", product_product.id, "image"
        )
        odoo_image_medium_url = self._get_odoo_image_url(
            "product.product", product_product.id, "image_medium"
        )
        odoo_image_small_url = self._get_odoo_image_url(
            "product.product", product_product.id, "image_small"
        )

        self.authenticate("demo", "demo")

        redirected_image = self.url_open(odoo_image_url, timeout=30)
        redirected_image_medium = self.url_open(odoo_image_medium_url, timeout=30)
        redirected_image_small = self.url_open(odoo_image_small_url, timeout=30)

        self.assertEqual(redirected_image.status_code, 200)
        self.assertEqual(redirected_image_medium.status_code, 200)
        self.assertEqual(redirected_image_small.status_code, 200)

        redirected_image_url = redirected_image.url
        redirected_image_medium_url = redirected_image_medium.url
        redirected_image_small_url = redirected_image_small.url

        # Attachments must be created during the execution of requests that are written above.
        product_product_image_variant_attachment = env[
            "ir.http"
        ]._find_field_attachment(
            env, "product.product", "image_variant", product_product.id
        )
        product_product_image_attachment = env["ir.http"]._find_field_attachment(
            env, "product.product", "image", product_product.id
        )
        product_product_image_medium_attachment = env["ir.http"]._find_field_attachment(
            env, "product.product", "image_medium", product_product.id
        )
        product_product_image_small_attachment = env["ir.http"]._find_field_attachment(
            env, "product.product", "image_small", product_product.id
        )

        a = set(
            product_product_image_variant_attachment.resized_ids.mapped(
                "resized_attachment_id"
            )
        )
        b = {
            product_product_image_attachment,
            product_product_image_medium_attachment,
            product_product_image_small_attachment,
        }
        self.assertFalse(a.difference(b))

        self.assertTrue(product_product_image_attachment)
        self.assertTrue(product_product_image_medium_attachment)
        self.assertTrue(product_product_image_small_attachment)

        self.assertEqual(redirected_image_url, product_product_image_attachment.url)
        self.assertEqual(
            redirected_image_medium_url, product_product_image_medium_attachment.url
        )
        self.assertEqual(
            redirected_image_small_url, product_product_image_small_attachment.url
        )

        urls = [
            self.original_image_url,
            redirected_image_url,
            redirected_image_medium_url,
            redirected_image_small_url,
        ]
        self.assertEqual(len(urls), len(set(urls)), "Duplicates in URLs: %s" % urls)

    def test_unlink_resized_attachments_when_parent_unlink(self):
        env = api.Environment(self.registry.test_cr, self.uid, {})

        ir_att_model = env["ir.attachment"]
        ir_att_resized_model = env["ir.attachment.resized"]

        original_att = ir_att_model.create({"name": "test att"})
        resized_att = ir_att_model.create({"name": "resized test att"})

        ir_att_resized = ir_att_resized_model.create(
            {"attachment_id": original_att.id, "resized_attachment_id": resized_att.id}
        )

        self.assertTrue(original_att.unlink())

        with self.assertRaises(exceptions.MissingError):
            original_att.write({"name": "foo"})

        with self.assertRaises(exceptions.MissingError):
            ir_att_resized.write({"width": 1})

        with self.assertRaises(exceptions.MissingError):
            resized_att.write({"name": "bar"})
