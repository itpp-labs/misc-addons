# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/molotov>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.odoo_backup_sh.tests.test_odoo_backup_sh_ui import TestUi as BaseTestUi


class TestUi(BaseTestUi):
    def test_odoo_backup_sh_tour(self):
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        self.env["ir.module.module"].search(
            [("name", "=", "odoo_backup_sh")], limit=1
        ).state = "installed"
        self.env["ir.module.module"].search(
            [("name", "=", "odoo_backup_sh_dropbox")], limit=1
        ).state = "installed"
        self.phantom_js(
            "/web",
            "odoo.__DEBUG__.services['web_tour.tour'].run('odoo_backup_sh_tour')",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.odoo_backup_sh_tour.ready",
            login="admin",
        )
