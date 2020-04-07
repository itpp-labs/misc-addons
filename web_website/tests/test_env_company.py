# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo.tests import common, tagged

_logger = logging.getLogger(__name__)


@tagged("at_install", "post_install")
class TestEnvCompany(common.TransactionCase):
    def test_env(self):
        companyA = self.env["res.company"].create({"name": "A"})
        websiteA = self.env["website"].create(
            {"name": "Website A", "company_id": companyA.id}
        )

        env = self.env["res.users"].with_context(website_id=websiteA.id).env
        self.assertEqual(
            env.company, companyA, "env.company doesn't depend on website_id in context"
        )

        # Check that there is no error on reading company without website context
        self.assertTrue(self.env.company)
