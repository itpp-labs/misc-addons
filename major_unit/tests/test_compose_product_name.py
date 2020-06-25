from odoo.tests import common


class TestComposeProductName(common.TransactionCase):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestComposeProductName, self).setUp()

        self.product_product_model = self.env['product.product']
        self.product_template_model = self.env['product.template']
        self.product_attribute_line_model = self.env['product.attribute.line']
        self.product_attribute_value_model = self.env['product.attribute.value']
        self.product_fitment_model = self.env['product.fitment']

        self.product_attr_year_name = 'YEAR'
        self.product_attr_make_name = 'MAKE'
        self.product_attr_model_name = 'MODEL'
        self.expected_name = 'YEAR MAKE MODEL'

    def test_compose_product_template_name(self):
        category = self.env.ref('major_unit.quartet_product_category_major_units')
        product_tmpl = self.product_template_model\
            .with_context({'create_product_product': False})\
            .create({
                'name': 'Badger',
                'details_model': 'vehicle',
                'categ_id': category.id,
            })
        year_attr = self.env.ref(self.product_fitment_model._product_attribute_year)
        make_attr = self.env.ref(self.product_fitment_model._product_attribute_make)
        model_attr = self.env.ref(self.product_fitment_model._product_attribute_model)

        year_line_value = self.product_attribute_value_model.create({
            'attribute_id': year_attr.id,
            'name': self.product_attr_year_name,
        })
        make_line_value = self.product_attribute_value_model.create({
            'attribute_id': make_attr.id,
            'name': self.product_attr_make_name,
        })
        model_line_value = self.product_attribute_value_model.create({
            'attribute_id': model_attr.id,
            'name': self.product_attr_model_name,
        })
        product_tmpl.write({
            'attribute_line_ids': [
                (0, 0, {'product_tmpl_id': product_tmpl.id, 'attribute_id': year_attr.id, 'value_ids': [(4, year_line_value.id)]}),
                (0, 0, {'product_tmpl_id': product_tmpl.id, 'attribute_id': make_attr.id, 'value_ids': [(4, make_line_value.id)]}),
                (0, 0, {'product_tmpl_id': product_tmpl.id, 'attribute_id': model_attr.id, 'value_ids': [(4, model_line_value.id)]}),
            ],
        })

        self.assertEqual(product_tmpl.name, self.expected_name, product_tmpl.get_stripped_year_make_model())

    def test_compose_product_product_name(self):
        year_attr = self.env.ref(self.product_fitment_model._product_attribute_year)
        make_attr = self.env.ref(self.product_fitment_model._product_attribute_make)
        model_attr = self.env.ref(self.product_fitment_model._product_attribute_model)

        year_value = self.product_attribute_value_model.create({
            'attribute_id': year_attr.id,
            'name': self.product_attr_year_name,
        })
        make_value = self.product_attribute_value_model.create({
            'attribute_id': make_attr.id,
            'name': self.product_attr_make_name,
        })
        model_value = self.product_attribute_value_model.create({
            'attribute_id': model_attr.id,
            'name': self.product_attr_model_name,
        })

        category = self.env.ref('major_unit.quartet_product_category_major_units')
        product = self.product_product_model.create({
            'name': 'Badger',
            'details_model': 'vehicle',
            'categ_id': category.id,
            'attribute_value_ids': [
                (4, year_value.id),
                (4, make_value.id),
                (4, model_value.id),
            ]
        })
        self.assertEqual(product.name, self.expected_name, product.get_stripped_year_make_model())
