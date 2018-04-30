from odoo.tests import common


class TestBase(common.TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestBase, self).setUp()
        self.config_param = self.env['ir.config_parameter']
        self.main_company = self.env.user.company_id
        self.second_company = self.env['res.company'].create({'name': 'Second company'})

    def test_cache(self):
        KEY = 'test_key'
        VALUE1 = 'value1'
        VALUE2 = 'value2'

        # set value for first company
        self.config_param.set_param(KEY, VALUE1)
        # call get_param to cache the value
        self.assertEqual(self.config_param.get_param(KEY), VALUE1, 'Value is not saved!')

        # set value for second company
        self.env.user.company_id = self.second_company
        self.config_param.set_param(KEY, VALUE2)
        param = self.config_param.search([('key', '=', KEY)])

        # check without cache first
        self.assertEqual(param.value, VALUE2, 'Value for second company is not saved!')

        # check cache
        self.assertEqual(self.config_param.get_param(KEY), VALUE2, 'Cache gives value for wrong company!')

        self.env.user.company_id = self.main_company
        self.assertEqual(self.config_param.get_param(KEY), VALUE1)
