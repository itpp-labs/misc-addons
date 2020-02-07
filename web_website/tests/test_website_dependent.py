# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo.tests import common, tagged

_logger = logging.getLogger(__name__)


@tagged("at_install", "post_install")
class TestFields(common.TransactionCase):
    def setUp(self):
        super(TestFields, self).setUp()
        self.MODEL_WEBSITE_DEPENDENT = "test.website_dependent"
        self.field = self.env["ir.model.fields"].search(
            [("model", "=", self.MODEL_WEBSITE_DEPENDENT), ("name", "=", "foo")]
        )

    def test_website_dependent(self):
        """ test website-dependent fields. """
        MODEL = "test.website_dependent"

        # consider three website
        website0 = self.env.ref("website.default_website")
        website1 = self.env.ref("website.website2")
        website2 = self.env["website"].create({"name": "Extra Website"})
        context0 = dict(website_id=website0.id)
        context1 = dict(website_id=website1.id)
        context2 = dict(website_id=website2.id)
        # create a default value for the website-dependent field
        field = self.env["ir.model.fields"].search(
            [("model", "=", MODEL), ("name", "=", "foo")]
        )
        self.env["ir.property"].create(
            {"name": "foo", "fields_id": field.id, "value": "default", "type": "char"}
        )

        # Default and website specific values
        record = self.env[MODEL].with_context(context0).create({"foo": "main"})
        record.invalidate_cache()
        self.assertEqual(record.with_context(context0).foo, "main")
        self.assertEqual(record.with_context(context1).foo, "default")
        self.assertEqual(record.with_context(context2).foo, "default")

        record.with_context(context1).foo = "alpha"
        record.invalidate_cache()
        self.assertEqual(record.with_context(context0).foo, "main")
        self.assertEqual(record.with_context(context1).foo, "alpha")
        self.assertEqual(record.with_context(context2).foo, "default")

        # Default, company-specific and website-specific values
        _logger.info(
            "Default, company-specific and website-specific values, record {}".format(
                record
            )
        )
        record = self.env[MODEL].create({"foo": "nowebsite"})
        record.invalidate_cache()
        self.assertEqual(record.foo, "nowebsite")
        self.assertEqual(record.with_context(context1).foo, "nowebsite")
        self.assertEqual(record.with_context(context2).foo, "nowebsite")

        record.with_context(context1).foo = "alpha"
        record.invalidate_cache()
        self.assertEqual(record.foo, "nowebsite")
        self.assertEqual(record.with_context(context1).foo, "alpha")
        self.assertEqual(record.with_context(context2).foo, "nowebsite")

        # mostly for coverage of search_multi
        res = self.env[MODEL].search([("foo", "=", False)])
        self.assertFalse(res)

        # test many2one
        record = self.env[MODEL].create({"name": "Name", "user_id": self.env.user})
        record.invalidate_cache()
        self.assertEqual(record.user_id, self.env.user)

    def _create_property(self, vals, record=None):
        base_vals = {"name": "foo", "fields_id": self.field.id, "type": "char"}
        if record:
            base_vals["res_id"] = "{},{}".format(record._name, record.id)

        base_vals.update(vals)
        _logger.info("create property with vals {}".format(base_vals))
        return self.env["ir.property"].create(base_vals)

    def test_website_dependent_priority_all_websites(self):
        """ test section "How it works" in index.rst (All-website case) """
        MODEL = "test.website_dependent"

        company = self.env.user.company_id
        website = self.env.ref("website.default_website")
        record = self.env[MODEL].create({"foo": "new_record"})

        # remove auto created records to be sure
        props = self.env["ir.property"].search([("fields_id", "=", self.field.id)])
        props.unlink()
        # **Company** and **Resource** are empty (i.e. only **Field** is matched)
        self._create_property({"value": "only_field"})
        record.invalidate_cache()
        self.assertEqual(record.foo, "only_field")

        # **Company** is matched, **Resource** is empty
        self._create_property({"company_id": company.id, "value": "only_company"})
        record.invalidate_cache()
        self.assertEqual(record.foo, "only_company")

        # **Company** and **Resource**  are matched
        self._create_property(
            {"company_id": company.id, "value": "company_and_resource"}, record
        )
        record.invalidate_cache()
        self.assertEqual(record.foo, "company_and_resource")

        # check that website-specific records are ignored
        self._create_property({"website_id": website.id, "value": "only_website"})
        record.invalidate_cache()
        self.assertEqual(record.foo, "company_and_resource")

        self._create_property(
            {"website_id": website.id, "value": "website_and_resource"}, record
        )
        record.invalidate_cache()
        self.assertEqual(record.foo, "company_and_resource")

    def test_website_dependent_priority(self):
        """ test section "How it works" in index.rst """
        MODEL = "test.website_dependent"

        company = self.env.user.company_id
        wrong_company = self.env["res.company"].create({"name": "A"})
        website = self.env.ref("website.default_website")
        website.company_id = company
        record = self.env[MODEL].create({"foo": "new_record"})
        record = record.with_context(website_id=website.id)

        # remove auto created records to be sure
        props = self.env["ir.property"].search([("fields_id", "=", self.field.id)])
        props.unlink()

        # **Company**, **Resource** and **Website** are empty (i.e. only **Field** is matched)
        self._create_property({"value": "only_field"})
        record.invalidate_cache()
        self.assertEqual(record.foo, "only_field")

        # **Company** is matched, **Resource** and **Website** are empty
        self._create_property({"company_id": company.id, "value": "only_company"})
        record.invalidate_cache()
        self.assertEqual(record.foo, "only_company")

        # **Company** and **Resource**  are matched, **Website** is empty
        self._create_property(
            {"company_id": company.id, "value": "company_and_resource"}, record
        )
        record.invalidate_cache()
        self.assertEqual(record.foo, "company_and_resource")

        # **Website** is matched, **Resource** is empty
        prop = self._create_property(
            {"website_id": website.id, "value": "only_website"}
        )
        record.invalidate_cache()
        self.assertEqual(record.foo, "only_website")

        # Note, that when **Company** and **Website** are both set,
        # **Website**'s Company must be equal to **Company** or Empty.
        prop.unlink()
        self._create_property(
            {
                "website_id": website.id,
                "company_id": wrong_company.id,
                "value": "website_and_company",
            }
        )
        record.invalidate_cache()
        self.assertEqual(record.foo, "company_and_resource")

        # **Website** and **Resource** are matched
        prop = self._create_property(
            {"website_id": website.id, "value": "website_and_resource"}, record
        )
        record.invalidate_cache()
        self.assertEqual(record.foo, "website_and_resource")

        # Note, that when **Company** and **Website** are both set,
        # **Website**'s Company must be equal to **Company** or Empty.
        prop.unlink()
        prop = self._create_property(
            {
                "website_id": website.id,
                "company_id": wrong_company.id,
                "value": "website_company_resource",
            },
            record,
        )
        record.invalidate_cache()
        self.assertEqual(record.foo, "company_and_resource")

    def test_company_dependent(self):
        """ test company-dependent fields. It's the same test as in odoo core"""
        MODEL = "test.company_dependent"
        # consider three companies
        company0 = self.env.ref("base.main_company")
        company1 = self.env["res.company"].create(
            {"name": "A", "parent_id": company0.id}
        )
        company2 = self.env["res.company"].create(
            {"name": "B", "parent_id": company1.id}
        )
        # we assume that root user has company0
        self.env.user.company_id = company0
        # create one user per company
        user0 = self.env["res.users"].create(
            {
                "name": "Foo",
                "login": "foo",
                "company_id": company0.id,
                "company_ids": [],
            }
        )
        user1 = self.env["res.users"].create(
            {
                "name": "Bar",
                "login": "bar",
                "company_id": company1.id,
                "company_ids": [],
            }
        )
        user2 = self.env["res.users"].create(
            {
                "name": "Baz",
                "login": "baz",
                "company_id": company2.id,
                "company_ids": [],
            }
        )
        # create a default value for the company-dependent field
        field = self.env["ir.model.fields"].search(
            [("model", "=", MODEL), ("name", "=", "foo")]
        )
        self.env["ir.property"].create(
            {"name": "foo", "fields_id": field.id, "value": "default", "type": "char"}
        )

        # create/modify a record, and check the value for each user
        record = self.env[MODEL].create({"foo": "main"})
        record.invalidate_cache()
        self.assertEqual(record.sudo(user0).foo, "main")
        self.assertEqual(record.sudo(user1).foo, "default")
        self.assertEqual(record.sudo(user2).foo, "default")

        record.sudo(user1).foo = "alpha"
        record.invalidate_cache()
        self.assertEqual(record.sudo(user0).foo, "main")
        self.assertEqual(record.sudo(user1).foo, "alpha")
        self.assertEqual(record.sudo(user2).foo, "default")
