# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestKiosk(odoo.tests.HttpCase):
    def test_kiosk(self):
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env = self.env
        env["ir.module.module"].search(
            [("name", "=", "base_attendance")], limit=1
        ).state = "installed"
        # without a delay there might be problems on the steps whilst opening a POS
        # caused by a not yet loaded button's action
        self.phantom_js(
            "/web",
            "odoo.__DEBUG__.services['web_tour.tour'].run('test_kiosk_tour', 500)",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.test_kiosk_tour.ready",
            login="admin",
        )
