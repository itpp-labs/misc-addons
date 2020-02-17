# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License MIT (https://opensource.org/licenses/MIT).

import requests_mock

from odoo.tests.common import HOST, PORT, HttpCase, at_install, post_install

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@at_install(True)
@post_install(True)
class TestUi(HttpCase):
    def setUp(self):
        super(TestUi, self).setUp()

        self.fetch_dashboard_data_mock = requests_mock.Mocker(real_http=True)
        url = "http://{}:{}/odoo_backup_sh/fetch_dashboard_data".format(HOST, PORT)
        self.fetch_dashboard_data_mock.register_uri("GET", url, json={"configs": []})
        self.fetch_dashboard_data_mock.start()

        self.patcher_get_cloud_params = patch(
            "odoo.addons.odoo_backup_sh.controllers.main.BackupController.get_cloud_params",
            wraps=lambda *args, **kwargs: {},
        )
        self.patcher_get_cloud_params.start()

    def test_odoo_backup_sh_tour(self):
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        self.env["ir.module.module"].search(
            [("name", "=", "odoo_backup_sh")], limit=1
        ).state = "installed"
        self.phantom_js(
            "/web",
            "odoo.__DEBUG__.services['web_tour.tour'].run('odoo_backup_sh_tour')",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.odoo_backup_sh_tour.ready",
            login="admin",
        )

    def tearDown(self):
        self.fetch_dashboard_data_mock.stop()
        self.patcher_get_cloud_params.stop()
        super(TestUi, self).tearDown()
