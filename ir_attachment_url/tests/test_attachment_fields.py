# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import base64
import binascii

import requests

from odoo.tests.common import TransactionCase, tagged

TEST_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Turkmenistan.svg/320px-Flag_of_Turkmenistan.svg.png"


@tagged("at_install", "post_install")
class TestAttachmentFields(TransactionCase):
    def _test_end(self, test_record):
        self.assertEqual(test_record.image, TEST_URL)
        test_record.invalidate_cache(fnames=["image"])
        self.assertEqual(test_record.image, TEST_URL)

        test_record = self.env["res.country"].browse(test_record.id)
        test_record.invalidate_cache(fnames=["image"])

        r = requests.get(TEST_URL, timeout=5)
        r.raise_for_status()
        self.assertEqual(test_record.image, base64.b64encode(r.content))

    def test_write(self):
        test_record = self.env["res.country"].create(
            {"name": "Turkmenistan (Test record)"}
        )

        with self.assertRaises(binascii.Error):
            test_record.image = TEST_URL

        self.assertEqual(test_record.image, False)

        test_record = test_record.with_context(
            ir_attachment_url_fields="res.country.image"
        )
        test_record.image = TEST_URL
        self._test_end(test_record)

    def test_create(self):
        TEST_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Turkmenistan.svg/320px-Flag_of_Turkmenistan.svg.png"

        with self.assertRaises(binascii.Error):
            test_record = self.env["res.country"].create(
                {"name": "With invalid image", "image": TEST_URL}
            )

        test_record = (
            self.env["res.country"]
            .with_context(ir_attachment_url_fields="res.country.image")
            .create({"name": "Turkmenistan (Test Record)", "image": TEST_URL})
        )
        self._test_end(test_record)
