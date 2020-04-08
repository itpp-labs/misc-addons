# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from werkzeug.urls import Href

from odoo import api, exceptions
from odoo.tests.common import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestResizedAttachments(HttpCase):
    def test_getting_cached_images_instead_computing(self):
        env = api.Environment(self.registry.test_cr, self.uid, {})

        record = env.ref("product.product_product_9").product_tmpl_id
        href = Href("/web/image")
        field = "image_1920"
        model = record._name
        width = 300
        height = 300

        url = href(
            {
                "model": model,
                "id": record.id,
                "field": field,
                "width": width,
                "height": height,
            }
        )

        self.authenticate("demo", "demo")

        response = self.url_open(url, timeout=30)

        self.assertEqual(response.status_code, 200)

        # Attachments must be created during the execution of requests that are written above.
        attachment = (
            env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_field", "=", field),
                    ("res_model", "=", model),
                    ("res_id", "=", record.id),
                ]
            )
        )
        attachment.ensure_one()

        resized = attachment.get_resized_from_cache(width, height, crop=False)

        resized_attachment = env["ir.attachment"].browse(
            resized.resized_attachment_id.id
        )
        resized_attachment.check("read")

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
            original_att.datas  # pylint: disable=pointless-statement

        with self.assertRaises(exceptions.MissingError):
            ir_att_resized.attachment_id  # pylint: disable=pointless-statement

        with self.assertRaises(exceptions.MissingError):
            resized_att.datas  # pylint: disable=pointless-statement
