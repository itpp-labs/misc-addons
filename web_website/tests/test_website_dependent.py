# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests import common


class TestFields(common.TransactionCase):

    at_install = True
    post_install = True

    def setUp(self):
        super(TestFields, self).setUp()
        self.field = self.env['ir.model.fields'].search([
            ('model', '=', MODEL),
            ('name', '=', 'foo')])

    def test_website_dependent(self):
        """ test website-dependent fields. """
        MODEL = 'test.website_dependent'

        # consider three website
        website0 = self.env.ref('website.default_website')
        website1 = self.env.ref('website.website2')
        website2 = self.env['website'].create({'name': 'Extra Website'})
        context0 = dict(website_id=website0.id)
        context1 = dict(website_id=website1.id)
        context2 = dict(website_id=website2.id)
        # create a default value for the website-dependent field
        field = self.env['ir.model.fields'].search([('model', '=', MODEL),
                                                    ('name', '=', 'foo')])
        self.env['ir.property'].create({'name': 'foo', 'fields_id': field.id,
                                        'value': 'default', 'type': 'char'})

        # Default and website specific values
        record = self.env[MODEL].with_context(context0).create({'foo': 'main'})
        record.invalidate_cache()
        self.assertEqual(record.with_context(context0).foo, 'main')
        self.assertEqual(record.with_context(context1).foo, 'default')
        self.assertEqual(record.with_context(context2).foo, 'default')

        record.with_context(context1).foo = 'alpha'
        record.invalidate_cache()
        self.assertEqual(record.with_context(context0).foo, 'main')
        self.assertEqual(record.with_context(context1).foo, 'alpha')
        self.assertEqual(record.with_context(context2).foo, 'default')

        # Default, company-specific and website-specific values
        record = self.env[MODEL].create({'foo': 'nowebsite'})
        record.invalidate_cache()
        self.assertEqual(record.foo, 'nowebsite')
        self.assertEqual(record.with_context(context1).foo, 'nowebsite')
        self.assertEqual(record.with_context(context2).foo, 'nowebsite')

        record.with_context(context1).foo = 'alpha'
        record.invalidate_cache()
        self.assertEqual(record.foo, 'nowebsite')
        self.assertEqual(record.with_context(context1).foo, 'alpha')
        self.assertEqual(record.with_context(context2).foo, 'nowebsite')

    def _create_property(self, vals, record=None):
        base_vals = {
            'name': 'foo',
            'fields_id': self.field.id,
            'type': 'char',
        }
        if record:
            base_vals['res_id'] = '%s,%s' % (record._name, record.id)

        return self.env['ir.property'].create(
            dict(base_vals.items() + vals.items())
        )

    def test_website_dependent_priority(self):
        """ test section "How it works" in index.rst """
        MODEL = 'test.website_dependent'

        company = self.env.user.company_id
        website = self.env.ref('website.default_website')
        record = self.env[MODEL].create({'foo': 'new_record'})

        # remove auto created records to be sure
        props = self.env['ir.property'].search([
            ('fields_id', '=', self.field.id),
        ])
        props.unlink()

        self._create_property({
            'value': 'only_field',
        })
        record.invalidate_cache()
        self.assertEqual(record.foo, 'only_field')

        # TOBECONTINUED

    def test_company_dependent(self):
        """ test company-dependent fields. It's the same test as in odoo core"""
        MODEL = 'test.company_dependent'
        # consider three companies
        company0 = self.env.ref('base.main_company')
        company1 = self.env['res.company'].create({'name': 'A', 'parent_id': company0.id})
        company2 = self.env['res.company'].create({'name': 'B', 'parent_id': company1.id})
        # create one user per company
        user0 = self.env['res.users'].create({'name': 'Foo', 'login': 'foo',
                                              'company_id': company0.id, 'company_ids': []})
        user1 = self.env['res.users'].create({'name': 'Bar', 'login': 'bar',
                                              'company_id': company1.id, 'company_ids': []})
        user2 = self.env['res.users'].create({'name': 'Baz', 'login': 'baz',
                                              'company_id': company2.id, 'company_ids': []})
        # create a default value for the company-dependent field
        field = self.env['ir.model.fields'].search([('model', '=', MODEL),
                                                    ('name', '=', 'foo')])
        self.env['ir.property'].create({'name': 'foo', 'fields_id': field.id,
                                        'value': 'default', 'type': 'char'})

        # create/modify a record, and check the value for each user
        record = self.env[MODEL].create({'foo': 'main'})
        record.invalidate_cache()
        self.assertEqual(record.sudo(user0).foo, 'main')
        self.assertEqual(record.sudo(user1).foo, 'default')
        self.assertEqual(record.sudo(user2).foo, 'default')

        record.sudo(user1).foo = 'alpha'
        record.invalidate_cache()
        self.assertEqual(record.sudo(user0).foo, 'main')
        self.assertEqual(record.sudo(user1).foo, 'alpha')
        self.assertEqual(record.sudo(user2).foo, 'default')
