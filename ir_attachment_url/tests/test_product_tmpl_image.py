# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api
from odoo.tests.common import HttpCase

_logger = logging.getLogger(__name__)


class TestProductTmplImage(HttpCase):
    at_install = False
    post_install = True

    def _get_original_image_url(self, px=1024):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Gullfoss%2C_an_iconic_waterfall_of_Iceland.jpg/{}px-Gullfoss%2C_an_iconic_waterfall_of_Iceland.jpg".format(
            px
        )

    def _get_odoo_image_url(self, model, record_id, field):
        return "/web/image?model={}&id={}&field={}".format(model, record_id, field)

    def test_getting_product_variant_image_fields_urls(self):
        env = api.Environment(self.registry.test_cr, self.uid, {})

        ir_attachment_url_storage = env["ir.config_parameter"].get_param(
            "ir_attachment_url.storage", default="url"
        )
        if ir_attachment_url_storage != "url":
            _logger.warning(
                "This test only works if the module has no add-ons! "
                "(ir_attachment_url_storage = %s)" % ir_attachment_url_storage
            )
            return

        product_tmpl = env["product.template"].create(
            {
                "name": "Test template",
                "image": self._get_original_image_url(1024),
                "image_medium": self._get_original_image_url(128),
                "image_small": self._get_original_image_url(64),
            }
        )

        product_product = env["product.product"].create(
            {
                "name": "Test product",
                "image": False,
                "image_medium": False,
                "image_small": False,
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

        product_tmpl_image_attachment = env["ir.http"].find_field_attachment(
            env, "product.template", "image", product_tmpl
        )
        product_tmpl_image_medium_attachment = env["ir.http"].find_field_attachment(
            env, "product.template", "image_medium", product_tmpl
        )
        product_tmpl_image_small_attachment = env["ir.http"].find_field_attachment(
            env, "product.template", "image_small", product_tmpl
        )

        self.assertTrue(product_tmpl_image_attachment)
        self.assertTrue(product_tmpl_image_medium_attachment)
        self.assertTrue(product_tmpl_image_small_attachment)

        self.authenticate("demo", "demo")

        self.assertEqual(
            self.url_open(odoo_image_url).geturl(), product_tmpl_image_attachment.url
        )
        self.assertEqual(
            self.url_open(odoo_image_medium_url).geturl(),
            product_tmpl_image_medium_attachment.url,
        )
        self.assertEqual(
            self.url_open(odoo_image_small_url).geturl(),
            product_tmpl_image_small_attachment.url,
        )
